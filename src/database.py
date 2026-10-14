
import sqlite3
from pathlib import Path
from contextlib import closing

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "baltic_it_skills.db"


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def create_tables():
    with closing(get_connection()) as conn:
        with conn:

            # 1. Уникальные вакансии MeetFrank
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

            # 2. Связь вакансий со странами
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

            # 3. Справочник навыков
            conn.execute("""
                CREATE TABLE IF NOT EXISTS skill (
                    skill_id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    first_seen_at TEXT
                )
            """)

            # 4. Связь вакансий с навыками
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

            # 5. История наблюдений
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
                )
            """)

    print("Database tables created successfully.")


if __name__ == "__main__":
    create_tables()
