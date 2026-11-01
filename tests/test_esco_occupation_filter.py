
import pytest

from src import database
from src.esco import filter_it_occupations as occupation_filter


@pytest.fixture
def test_db(tmp_path, monkeypatch):
    """Create an isolated SQLite database for classification tests."""

    db_path = tmp_path / "test_classification.db"
    monkeypatch.setattr(database, "DB_PATH", db_path)

    database.create_tables()

    with database.get_connection() as conn:
        conn.executemany(
            """
            INSERT INTO occupation (occupation_uri, title)
            VALUES (?, ?)
            """,
            [
                ("occupation:developer", "Software developer"),
                ("occupation:teacher", "Teacher"),
            ],
        )

    return db_path


@pytest.mark.parametrize(
    ("code", "expected"),
    [
        ("2512.1", True),
        ("2522", True),
        ("3512.1", True),
        ("1330.6", True),
        ("1330.7", True),
        ("2341", False),
        ("3115.1", False),
    ],
)
def test_ict_classification(code, expected):
    """Classify occupation codes using the configured ICT rules."""

    assert occupation_filter.is_ict_occupation(code) is expected


@pytest.mark.parametrize(
    "code",
    [
        "",
        "unknown",
        "25ABC",
        "2512.",
        "2512.1.abc",
    ],
)
def test_invalid_occupation_codes(code):
    """Reject malformed occupation codes."""

    with pytest.raises(ValueError):
        occupation_filter.validate_occupation_code(code)


def test_save_ict_classification(test_db):
    """Save an ICT occupation classification."""

    result = occupation_filter.save_occupation_classification(
        "occupation:developer",
        "2512.1",
    )

    assert result == "ICT"

    with database.get_connection() as conn:
        row = conn.execute(
            """
            SELECT isco_code, ict_category, fetched_at
            FROM occupation
            WHERE occupation_uri = ?
            """,
            ("occupation:developer",),
        ).fetchone()

    assert row[0] == "2512.1"
    assert row[1] == "ICT"
    assert row[2] is not None


def test_save_non_ict_classification(test_db):
    """Save a non-ICT occupation classification."""

    result = occupation_filter.save_occupation_classification(
        "occupation:teacher",
        "2341",
    )

    assert result == "non-ICT"


def test_processed_occupation_is_not_selected_again(test_db):
    """Exclude classified occupations from subsequent batches."""

    pending_before = occupation_filter.get_pending_occupations()

    assert len(pending_before) == 2

    occupation_filter.save_occupation_classification(
        "occupation:developer",
        "2512.1",
    )

    pending_after = occupation_filter.get_pending_occupations()

    assert len(pending_after) == 1
    assert pending_after[0][0] == "occupation:teacher"


def test_unknown_occupation_is_rejected(test_db):
    """Reject updates for occupations absent from the database."""

    with pytest.raises(ValueError, match="Occupation not found"):
        occupation_filter.save_occupation_classification(
            "occupation:missing",
            "2512.1",
        )
