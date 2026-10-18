
from contextlib import closing

from .database import get_connection


def migrate_observation_fk():
    with closing(get_connection()) as conn:
        # Проверяем, существует ли внешний ключ
        foreign_keys = conn.execute(
            "PRAGMA foreign_key_list(job_observation)"
        ).fetchall()

        if any(
            row[2] == "pipeline_run" and row[3] == "run_id"
            for row in foreign_keys
        ):
            print("Foreign key already exists.")
            return

        # Проверяем, нет ли ссылок на несуществующие запуски
        invalid = conn.execute("""
            SELECT COUNT(*)
            FROM job_observation AS o
            LEFT JOIN pipeline_run AS p
                ON o.run_id = p.run_id
            WHERE o.run_id IS NOT NULL
              AND p.run_id IS NULL
        """).fetchone()[0]

        if invalid:
            raise ValueError(
                f"Found {invalid} observations with invalid run_id"
            )

        before = conn.execute(
            "SELECT COUNT(*) FROM job_observation"
        ).fetchone()[0]

        with conn:
            conn.execute("""
                CREATE TABLE job_observation_new (
                    job_obs_id INTEGER PRIMARY KEY,
                    job_id TEXT NOT NULL,
                    country TEXT NOT NULL,
                    observed_date TEXT NOT NULL,
                    run_id INTEGER,
                    skill_hash TEXT NOT NULL,
                    skills_snapshot TEXT NOT NULL,

                    UNIQUE(job_id, country, observed_date),

                    FOREIGN KEY (job_id, country)
                        REFERENCES job_countries(job_id, country),

                    FOREIGN KEY (run_id)
                        REFERENCES pipeline_run(run_id)
                )
            """)

            conn.execute("""
                INSERT INTO job_observation_new (
                    job_obs_id, job_id, country,
                    observed_date, run_id,
                    skill_hash, skills_snapshot
                )
                SELECT
                    job_obs_id, job_id, country,
                    observed_date, run_id,
                    skill_hash, skills_snapshot
                FROM job_observation
            """)

            after = conn.execute(
                "SELECT COUNT(*) FROM job_observation_new"
            ).fetchone()[0]

            if before != after:
                raise ValueError("Observation count mismatch!")

            conn.execute("DROP TABLE job_observation")

            conn.execute("""
                ALTER TABLE job_observation_new
                RENAME TO job_observation
            """)

            errors = conn.execute(
                "PRAGMA foreign_key_check"
            ).fetchall()

            if errors:
                raise ValueError(
                    f"Foreign key errors: {errors}"
                )

    print(f"Migration successful! Preserved {before} observations.")


if __name__ == "__main__":
    migrate_observation_fk()
