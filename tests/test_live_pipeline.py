from tempfile import TemporaryDirectory
from pathlib import Path
from unittest.mock import patch
from contextlib import closing

from src.database import get_connection, create_tables
from src.fetch_meetfrank import fetch_all_jobs
from src.update_meetfrank import update_meetfrank


def test_live_pipeline():
    jobs = fetch_all_jobs()

    with TemporaryDirectory() as temp_dir:
        test_db = Path(temp_dir) / "test.db"

        with patch("src.database.DB_PATH", test_db):
            create_tables()
            update_meetfrank(jobs)
            update_meetfrank(jobs)
            with closing(get_connection()) as conn:
                for table in ["job", "job_countries", "skill",
                            "job_skill", "job_observation"]:
                    count = conn.execute(
                        f"SELECT COUNT(*) FROM {table}"
                    ).fetchone()[0]
                    print(f"{table}: {count}")
                assert conn.execute(
                    "SELECT COUNT(*) FROM job"
                ).fetchone()[0] == len(set(job["id"] for job in jobs))
                assert conn.execute(
                    "SELECT COUNT(*) FROM job_countries"
                ).fetchone()[0] == len(jobs)
                assert conn.execute(
                    "SELECT COUNT(*) FROM job_observation"
                ).fetchone()[0] == len(jobs)


if __name__ == "__main__":
    test_live_pipeline()