
import sqlite3
import json

from src.observations import save_observation
from src.job_skills import sync_job_skills


def test_observation_history():
    # Create an in-memory database for testing
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON")

    try:
        # Create the minimal database schema required for the test
        conn.executescript("""
            CREATE TABLE job (
                job_id TEXT PRIMARY KEY NOT NULL
            );

            CREATE TABLE job_countries (
                job_id TEXT NOT NULL,
                country TEXT NOT NULL,
                PRIMARY KEY (job_id, country),
                FOREIGN KEY (job_id) REFERENCES job(job_id)
            );

            CREATE TABLE skill (
                skill_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                first_seen_at TEXT
            );

            CREATE TABLE job_skill (
                job_id TEXT NOT NULL,
                skill_id INTEGER NOT NULL,
                PRIMARY KEY (job_id, skill_id),
                FOREIGN KEY (job_id) REFERENCES job(job_id),
                FOREIGN KEY (skill_id) REFERENCES skill(skill_id)
            );

            CREATE TABLE job_observation (
                job_obs_id INTEGER PRIMARY KEY,
                job_id TEXT NOT NULL,
                country TEXT NOT NULL,
                observed_date TEXT NOT NULL,
                run_id INTEGER,
                skill_hash TEXT,
                skills_snapshot TEXT,
                UNIQUE (job_id, country, observed_date),
                FOREIGN KEY (job_id, country)
                    REFERENCES job_countries(job_id, country)
            );
        """)

        # Insert a sample job and its country association
        conn.execute("INSERT INTO job VALUES ('1001')")
        conn.execute(
            "INSERT INTO job_countries VALUES ('1001', 'estonia')"
        )

        # Day 1: Initial skills are Python and Docker
        sync_job_skills(
            conn, "1001", ["Python", "Docker"], "2026-10-12"
        )
        save_observation(
            conn, "1001", "estonia",
            ["Python", "Docker"], "2026-10-12"
        )

        # Day 2: The skill set remains unchanged
        sync_job_skills(
            conn, "1001", ["Python", "Docker"], "2026-10-13"
        )
        save_observation(
            conn, "1001", "estonia",
            ["Python", "Docker"], "2026-10-13"
        )

        # Day 3: Docker is replaced with Kubernetes
        sync_job_skills(
            conn, "1001", ["Python", "Kubernetes"], "2026-10-14"
        )
        save_observation(
            conn, "1001", "estonia",
            ["Python", "Kubernetes"], "2026-10-14"
        )

        # Repeat the observation for Day 3 to verify deduplication
        save_observation(
            conn, "1001", "estonia",
            ["Python", "Kubernetes"], "2026-10-14"
        )

        # Retrieve the current skills associated with the job
        current = [
            row[0] for row in conn.execute("""
                SELECT s.name
                FROM job_skill js
                JOIN skill s ON s.skill_id = js.skill_id
                ORDER BY s.name
            """)
        ]

        # Retrieve the historical skill snapshots
        history = [
            (day, json.loads(snapshot))
            for day, snapshot in conn.execute("""
                SELECT observed_date, skills_snapshot
                FROM job_observation
                ORDER BY observed_date
            """)
        ]

        # Verify that only the latest skills remain active
        assert current == ["Kubernetes", "Python"]

        # Verify that duplicate observations are not created
        assert len(history) == 3

        # Verify that historical skill snapshots are preserved
        assert history[0][1] == ["Docker", "Python"]
        assert history[2][1] == ["Kubernetes", "Python"]

    finally:
        # Close the in-memory database connection
        conn.close()
