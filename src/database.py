
from datetime import datetime, timezone
import sqlite3
from contextlib import closing

from .logger import get_logger
from .config import DB_PATH

logger = get_logger(__name__)


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def create_tables():
    with closing(get_connection()) as conn:
        with conn:

            # 1. Unique MeetFrank job postings
            conn.execute("""
                CREATE TABLE IF NOT EXISTS job (
                    job_id TEXT PRIMARY KEY NOT NULL,
                    title TEXT,
                    company TEXT,
                    location TEXT,
                    remote_type TEXT,
                    speciality TEXT,
                    seniorities TEXT,
                    employment_type TEXT,
                    published_at TEXT,
                    apply_url TEXT,
                    first_seen_at TEXT,
                    last_seen_at TEXT
                )
            """)

            # 2. Relationship between jobs and countries
            conn.execute("""
                CREATE TABLE IF NOT EXISTS job_countries (
                    job_id TEXT NOT NULL,
                    country TEXT NOT NULL,
                    first_seen_at TEXT,
                    last_seen_at TEXT,

                    PRIMARY KEY (job_id, country),
                    FOREIGN KEY (job_id)
                        REFERENCES job(job_id)
                )
            """)

            # 3. Skill reference table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS skill (
                    skill_id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    first_seen_at TEXT
                )
            """)

            # 4. Relationship between jobs and skills
            conn.execute("""
                CREATE TABLE IF NOT EXISTS job_skill (
                    job_id TEXT NOT NULL,
                    skill_id INTEGER NOT NULL,

                    PRIMARY KEY (job_id, skill_id),

                    FOREIGN KEY (job_id)
                        REFERENCES job(job_id),

                    FOREIGN KEY (skill_id)
                        REFERENCES skill(skill_id)
                )
            """)

            # 5. Store information about each pipeline run
            conn.execute("""
                CREATE TABLE IF NOT EXISTS pipeline_run (
                    run_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    started_at TEXT NOT NULL,
                    finished_at TEXT,
                    status TEXT NOT NULL
                        CHECK(status IN ('running', 'success', 'partial', 'failed')),
                    new_jobs INTEGER DEFAULT 0,
                    updated_jobs INTEGER DEFAULT 0,
                    new_skills INTEGER DEFAULT 0,
                    error_message TEXT
                )
            """)

            # 6. Job observation history
            conn.execute("""
                CREATE TABLE IF NOT EXISTS job_observation (
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
                    FOREIGN KEY (run_id)
                        REFERENCES pipeline_run(run_id)
                )
            """)


            # 7. Store pipeline results for each country
            conn.execute("""
                CREATE TABLE IF NOT EXISTS pipeline_run_countries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id INTEGER NOT NULL,
                    country TEXT NOT NULL,
                    status TEXT NOT NULL
                        CHECK(status IN ('success', 'failed')),
                    records_received INTEGER DEFAULT 0,
                    error_message TEXT,

                    FOREIGN KEY (run_id)
                        REFERENCES pipeline_run(run_id),

                    UNIQUE(run_id, country)
                )
            """)

            # 8. ESCO skill reference table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS esco_skill (
                    esco_uri TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    version TEXT,
                    fetched_at TEXT
                );
            """)
            
            # 9. ESCO occupation reference table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS occupation (
                    occupation_uri TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    isco_code TEXT,
                    ict_category TEXT,
                    fetched_at TEXT
                );
            """)

            # 10. Mapping between MeetFrank skills and ESCO skills
            conn.execute("""
                CREATE TABLE IF NOT EXISTS skill_mapping (
                    skill_id INTEGER PRIMARY KEY,
                    esco_uri TEXT,
                    status TEXT NOT NULL
                        CHECK (status IN ('exact', 'broader', 'review')),
                    mapping_method TEXT,
                    reviewed_at TEXT,
                    FOREIGN KEY (skill_id) REFERENCES skill(skill_id),
                    FOREIGN KEY (esco_uri) REFERENCES esco_skill(esco_uri)
                );
            """)

            # 11. Relationship between ESCO skills and occupations
            conn.execute("""
                    CREATE TABLE IF NOT EXISTS esco_skill_occupation (
                    esco_uri TEXT NOT NULL,
                    occupation_uri TEXT NOT NULL,
                    relation_type TEXT,
                    PRIMARY KEY (esco_uri, occupation_uri),
                    FOREIGN KEY (esco_uri) REFERENCES esco_skill(esco_uri),
                    FOREIGN KEY (occupation_uri) REFERENCES occupation(occupation_uri)
                );
            """)

            # 12. History of MeetFrank skill checks against ESCO
            conn.execute("""
                CREATE TABLE IF NOT EXISTS esco_check (
                    skill_id INTEGER PRIMARY KEY,
                    status TEXT NOT NULL
                        CHECK(status IN ('exact', 'no_match')),
                    checked_at TEXT NOT NULL,
                    esco_version TEXT NOT NULL,
                    FOREIGN KEY (skill_id)
                        REFERENCES skill(skill_id)
                )
            """)

    logger.info("Database tables created successfully.")

def start_pipeline_run():
    started_at = datetime.now(timezone.utc).isoformat()

    with closing(get_connection()) as conn:
        with conn:
            cursor = conn.execute("""
                INSERT INTO pipeline_run (started_at, status)
                VALUES (?, ?)
            """, (started_at, "running"))

            run_id = cursor.lastrowid

    return run_id

def finish_pipeline_run(run_id, status, error_message=None):
    finished_at = datetime.now(timezone.utc).isoformat()

    with closing(get_connection()) as conn:
        with conn:
            conn.execute("""
                UPDATE pipeline_run
                SET finished_at = ?,
                    status = ?,
                    error_message = ?
                WHERE run_id = ?
            """, (finished_at, status, error_message, run_id))

def save_country_run(run_id, country, status, records_received=0, error_message=None):
    with closing(get_connection()) as conn:
        with conn:
            conn.execute("""
                INSERT INTO pipeline_run_countries (
                    run_id, country, status,
                    records_received, error_message
                )
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(run_id, country) DO UPDATE SET
                    status = excluded.status,
                    records_received = excluded.records_received,
                    error_message = excluded.error_message
            """, (
                run_id, country, status,
                records_received, error_message
            ))

def save_pipeline_stats(run_id, stats):
    with closing(get_connection()) as conn:
        with conn:
            conn.execute("""
                UPDATE pipeline_run
                SET new_jobs = ?,
                    updated_jobs = ?,
                    new_skills = ?
                WHERE run_id = ?
            """, (
                stats["new_jobs"],
                stats["updated_jobs"],
                stats["new_skills"],
                run_id
            ))

if __name__ == "__main__":
    create_tables()
