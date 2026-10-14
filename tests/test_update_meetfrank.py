
import json
import sqlite3
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch
from contextlib import closing

from src.database import create_tables
from src.update_meetfrank import update_meetfrank


# Создаём временную базу, которая удалится после теста
with tempfile.TemporaryDirectory() as temp_dir:
    test_db = Path(temp_dir) / "test.db"

    def test_connection():
        conn = sqlite3.connect(test_db)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    # Подменяем подключение к настоящей базе тестовым
    with patch("src.database.DB_PATH", test_db):
        create_tables()

        job = {
            "id": "TEST-001",
            "country": "estonia",
            "title": "Python Developer",
            "company": "Test Company",
            "location": "Tallinn",
            "remote_type": "remote",
            "speciality": "software engineering",
            "seniorities": ["junior"],
            "employment_type": "full-time",
            "published_at": None,
            "apply_url": None,
            "skills": ["Python", "Docker"]
        }

        # Первое наблюдение
        update_meetfrank(
            [job],
            datetime(2026, 10, 12, tzinfo=timezone.utc)
        )

        # Повторное наблюдение в тот же день
        update_meetfrank(
            [job],
            datetime(2026, 10, 12, tzinfo=timezone.utc)
        )

        # Навыки изменились
        changed_job = {
            **job,
            "skills": ["Python", "Kubernetes"]
        }

        update_meetfrank(
            [changed_job],
            datetime(2026, 10, 14, tzinfo=timezone.utc)
        )

        # Проверяем данные
        with closing(test_connection()) as conn:
            counts = {}

            for table in (
                "job",
                "job_countries",
                "skill",
                "job_skill",
                "job_observation"
            ):
                counts[table] = conn.execute(
                    f"SELECT COUNT(*) FROM {table}"
                ).fetchone()[0]

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

        print("\nTABLE COUNTS:", counts)
        print("CURRENT SKILLS:", current_skills)
        print("HISTORY:", history)

        assert counts == {
            "job": 1,
            "job_countries": 1,
            "skill": 3,
            "job_skill": 2,
            "job_observation": 2
        }

        assert current_skills == ["Kubernetes", "Python"]
        assert history[0][1] == ["Docker", "Python"]
        assert history[1][1] == ["Kubernetes", "Python"]

        print("\nALL UPDATE TESTS PASSED!")
        
        # ТЕСТ: одна вакансия в двух странах
        multi_job_ee = {
            **job,
            "id": "TEST-002",
            "country": "estonia",
            "title": "Fullstack Developer",
            "skills": ["Python", "React"]
        }

        multi_job_lv = {
            **multi_job_ee,
            "country": "latvia"
        }

        update_meetfrank(
            [multi_job_ee, multi_job_lv],
            datetime(2026, 10, 14, tzinfo=timezone.utc)
        )

        with closing(test_connection()) as conn:
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

        print("\nMULTICOUNTRY TEST")
        print("Jobs:", job_count)
        print("Countries:", countries)
        print("Observations:", observations)
        print("Skills:", skills)

        assert job_count == 1
        assert countries == ["estonia", "latvia"]
        assert observations == ["estonia", "latvia"]
        assert skills == ["Python", "React"]

        print("MULTICOUNTRY TEST PASSED!")

        
        # ТЕСТ: откат транзакции при ошибке

        good_job = {
            **job,
            "id": "TEST-ROLLBACK-1",
            "country": "estonia",
            "skills": ["Python"]
        }

        bad_job = {
            **job,
            "id": "TEST-ROLLBACK-2",
            "country": "latvia",
            "skills": ["Docker"]
        }

        # Специально создаём ошибку во второй вакансии:
        # список нельзя сохранить в обычное TEXT-поле SQLite
        bad_job["title"] = ["Invalid", "Title"]

        try:
            update_meetfrank(
                [good_job, bad_job],
                datetime(2026, 10, 14, tzinfo=timezone.utc)
            )
        except sqlite3.ProgrammingError as error:
            print("\nEXPECTED ERROR:", error)
        else:
            raise AssertionError("Expected database error did not occur")

        # Проверяем, что ни одна из двух вакансий не сохранилась
        with closing(test_connection()) as conn:
            remaining = conn.execute("""
                SELECT COUNT(*)
                FROM job
                WHERE job_id IN (
                    'TEST-ROLLBACK-1',
                    'TEST-ROLLBACK-2'
                )
            """).fetchone()[0]

        print("Jobs remaining after rollback:", remaining)

        assert remaining == 0

        print("ROLLBACK TEST PASSED!")
