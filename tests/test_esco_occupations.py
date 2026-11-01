
import sqlite3

import pytest

from src import database
from src.esco import fetch_occupations as occupations


@pytest.fixture
def test_db(tmp_path, monkeypatch):
    """Create an isolated SQLite database for occupation tests."""
    db_path = tmp_path / "test_occupations.db"

    monkeypatch.setattr(database, "DB_PATH", db_path)
    database.create_tables()

    with database.get_connection() as conn:
        conn.executemany(
            """
            INSERT INTO esco_skill (esco_uri, title)
            VALUES (?, ?)
            """,
            [
                ("skill:python", "Python"),
                ("skill:java", "Java"),
            ],
        )

    return db_path


def test_save_essential_and_optional_occupations(test_db):
    """Save both occupation relationship types."""
    data = {
        "_links": {
            "isEssentialForOccupation": [
                {"uri": "occupation:developer", "title": "Developer"}
            ],
            "isOptionalForOccupation": [
                {"uri": "occupation:tester", "title": "Tester"}
            ],
        }
    }

    count = occupations.save_skill_occupations("skill:python", data)

    assert count == 2

    with database.get_connection() as conn:
        rows = conn.execute(
            """
            SELECT occupation_uri, relation_type
            FROM esco_skill_occupation
            ORDER BY occupation_uri
            """
        ).fetchall()

    assert rows == [
        ("occupation:developer", "essential"),
        ("occupation:tester", "optional"),
    ]


def test_shared_occupation_is_not_duplicated(test_db):
    """Reuse an occupation referenced by multiple skills."""
    data = {
        "_links": {
            "isEssentialForOccupation": [
                {"uri": "occupation:developer", "title": "Developer"}
            ]
        }
    }

    occupations.save_skill_occupations("skill:python", data)
    occupations.save_skill_occupations("skill:java", data)

    with database.get_connection() as conn:
        occupation_count = conn.execute(
            "SELECT COUNT(*) FROM occupation"
        ).fetchone()[0]

        relation_count = conn.execute(
            "SELECT COUNT(*) FROM esco_skill_occupation"
        ).fetchone()[0]

    assert occupation_count == 1
    assert relation_count == 2


def test_empty_occupations_are_marked_as_fetched(test_db):
    """Record a successful response with no occupations."""
    data = {
        "_links": {
            "isEssentialForOccupation": [],
            "isOptionalForOccupation": [],
        }
    }

    count = occupations.save_skill_occupations("skill:python", data)

    assert count == 0

    with database.get_connection() as conn:
        row = conn.execute(
            """
            SELECT relation_count
            FROM esco_occupation_fetch
            WHERE esco_uri = ?
            """,
            ("skill:python",),
        ).fetchone()

    assert row == (0,)


def test_failed_save_rolls_back_transaction(test_db):
    """Do not mark a skill as fetched when saving fails."""
    data = {
        "_links": {
            "isEssentialForOccupation": [
                {"uri": "occupation:developer", "title": "Developer"}
            ]
        }
    }

    with pytest.raises(sqlite3.IntegrityError):
        occupations.save_skill_occupations("skill:missing", data)

    with database.get_connection() as conn:
        occupation_count = conn.execute(
            "SELECT COUNT(*) FROM occupation"
        ).fetchone()[0]

        fetch_count = conn.execute(
            "SELECT COUNT(*) FROM esco_occupation_fetch"
        ).fetchone()[0]

    assert occupation_count == 0
    assert fetch_count == 0



def test_fetched_skill_is_not_selected_again(test_db):
    """Exclude successfully fetched skills from the next batch."""

    with database.get_connection() as conn:
        conn.execute(
            """
            INSERT INTO skill (name)
            VALUES (?)
            """,
            ("Python",),
        )

        skill_id = conn.execute(
            "SELECT skill_id FROM skill WHERE name = ?",
            ("Python",),
        ).fetchone()[0]

        conn.execute(
            """
            INSERT INTO skill_mapping (
                skill_id,
                esco_uri,
                status
            )
            VALUES (?, ?, ?)
            """,
            (skill_id, "skill:python", "exact"),
        )

        conn.commit()

    pending_before = occupations.get_mapped_esco_skills(limit=20)

    assert "skill:python" in pending_before

    occupations.save_skill_occupations(
        "skill:python",
        {
            "_links": {
                "isEssentialForOccupation": [],
                "isOptionalForOccupation": [],
            }
        },
    )

    pending_after = occupations.get_mapped_esco_skills(limit=20)

    assert "skill:python" not in pending_after


def test_conflicting_occupation_relations_are_rejected(test_db):
    """Reject conflicting relationships without writing to SQLite."""

    data = {
        "_links": {
            "isEssentialForOccupation": [
                {
                    "uri": "occupation:developer",
                    "title": "Developer",
                }
            ],
            "isOptionalForOccupation": [
                {
                    "uri": "occupation:developer",
                    "title": "Developer",
                }
            ],
        }
    }

    with pytest.raises(ValueError, match="Conflicting"):
        occupations.save_skill_occupations("skill:python", data)

    with database.get_connection() as conn:
        occupation_count = conn.execute(
            "SELECT COUNT(*) FROM occupation"
        ).fetchone()[0]

        relation_count = conn.execute(
            "SELECT COUNT(*) FROM esco_skill_occupation"
        ).fetchone()[0]

        fetch_count = conn.execute(
            "SELECT COUNT(*) FROM esco_occupation_fetch"
        ).fetchone()[0]

    assert occupation_count == 0
    assert relation_count == 0
    assert fetch_count == 0
