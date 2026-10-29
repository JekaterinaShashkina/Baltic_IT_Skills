
import json
import sqlite3
from contextlib import closing
from datetime import datetime, timezone

import pytest

import src.database as database
from src.update_meetfrank import update_meetfrank


TEST_DATE = datetime(2026, 10, 12, tzinfo=timezone.utc)
CHANGED_DATE = datetime(2026, 10, 14, tzinfo=timezone.utc)


@pytest.fixture
def test_db(tmp_path, monkeypatch):
    # Create an isolated SQLite database for each test
    db_path = tmp_path / "test.db"

    # Redirect database connections to the temporary database
    monkeypatch.setattr(database, "DB_PATH", db_path)
    database.create_tables()

    return db_path


def make_job(job_id="TEST-001", country="estonia", skills=None):
    # Create a sample MeetFrank job
    return {
        "id": job_id,
        "country": country,
        "title": "Python Developer",
        "company": "Test Company",
        "location": "Tallinn",
        "remote_type": "remote",
        "speciality": "software engineering",
        "seniorities": ["junior"],
        "employment_type": "full-time",
        "published_at": None,
        "apply_url": None,
        "skills": ["Python", "Docker"] if skills is None else skills
    }


def test_job_skill_updates(test_db):
    job = make_job()

    # Save the initial observation
    update_meetfrank([job], TEST_DATE)

    # Repeat the observation on the same day
    update_meetfrank([job], TEST_DATE)

    # Replace Docker with Kubernetes
    changed_job = make_job(skills=["Python", "Kubernetes"])
    update_meetfrank([changed_job], CHANGED_DATE)

    with closing(sqlite3.connect(test_db)) as conn:
        counts = {
            table: conn.execute(
                f"SELECT COUNT(*) FROM {table}"
            ).fetchone()[0]
            for table in (
                "job",
                "job_countries",
                "skill",
                "job_skill",
                "job_observation"
            )
        }

        current_skills = [
            row[0] for row in conn.execute("""
                SELECT s.name
                FROM job_skill js
                JOIN skill s ON s.skill_id = js.skill_id
                ORDER BY s.name
            """)
        ]

        history = [
            (day, json.loads(snapshot))
            for day, snapshot in conn.execute("""
                SELECT observed_date, skills_snapshot
                FROM job_observation
                ORDER BY observed_date
            """)
        ]

    # Verify database records and current skills
    assert counts == {
        "job": 1,
        "job_countries": 1,
        "skill": 3,
        "job_skill": 2,
        "job_observation": 2
    }

    assert current_skills == ["Kubernetes", "Python"]

    # Verify historical snapshots and daily deduplication
    assert history[0][1] == ["Docker", "Python"]
    assert history[1][1] == ["Kubernetes", "Python"]


def test_multicountry_job(test_db):
    job_ee = make_job(
        job_id="TEST-002",
        country="estonia",
        skills=["Python", "React"]
    )

    job_lv = {
        **job_ee,
        "country": "latvia"
    }

    # Save the same job observed in two countries
    update_meetfrank([job_ee, job_lv], CHANGED_DATE)

    with closing(sqlite3.connect(test_db)) as conn:
        job_count = conn.execute("""
            SELECT COUNT(*)
            FROM job
            WHERE job_id = 'TEST-002'
        """).fetchone()[0]

        countries = [
            row[0] for row in conn.execute("""
                SELECT country
                FROM job_countries
                WHERE job_id = 'TEST-002'
                ORDER BY country
            """)
        ]

        observations = [
            row[0] for row in conn.execute("""
                SELECT country
                FROM job_observation
                WHERE job_id = 'TEST-002'
                ORDER BY country
            """)
        ]

        skills = [
            row[0] for row in conn.execute("""
                SELECT s.name
                FROM job_skill js
                JOIN skill s ON s.skill_id = js.skill_id
                WHERE js.job_id = 'TEST-002'
                ORDER BY s.name
            """)
        ]

    # Verify that the job is stored only once
    assert job_count == 1

    # Verify both country associations and observations
    assert countries == ["estonia", "latvia"]
    assert observations == ["estonia", "latvia"]
    assert skills == ["Python", "React"]


def test_transaction_rollback(test_db):
    good_job = make_job(
        job_id="TEST-ROLLBACK-1",
        skills=["Python"]
    )

    bad_job = make_job(
        job_id="TEST-ROLLBACK-2",
        country="latvia",
        skills=["Docker"]
    )

    # Use an invalid SQLite value to trigger an insertion error
    bad_job["title"] = ["Invalid", "Title"]

    # Verify that the database operation raises an error
    with pytest.raises(sqlite3.ProgrammingError):
        update_meetfrank([good_job, bad_job], CHANGED_DATE)

    with closing(sqlite3.connect(test_db)) as conn:
        remaining = conn.execute("""
            SELECT COUNT(*)
            FROM job
            WHERE job_id IN (
                'TEST-ROLLBACK-1',
                'TEST-ROLLBACK-2'
            )
        """).fetchone()[0]

    # Verify that the entire transaction was rolled back
    assert remaining == 0
