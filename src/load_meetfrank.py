
import json
from datetime import datetime, timezone, date
from pathlib import Path
import hashlib
from contextlib import closing
try:
    from .database import get_connection, create_tables
except ImportError:
    from database import get_connection, create_tables


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "processed" / "meetfrank_baltic_jobs.json"

def save_observation(conn, job_id, country, skills, observed_date):
    # Сортируем навыки, чтобы порядок не влиял на результат
    sorted_skills = sorted(set(skills))

    skills_json = json.dumps(
        sorted_skills,
        ensure_ascii=False
    )

    skills_hash = hashlib.sha256(
        skills_json.encode("utf-8")
    ).hexdigest()

    conn.execute("""
        INSERT INTO job_observation (
            job_id, country, observed_date,
            skill_hash, skills_snapshot
        )
        VALUES (?, ?, ?, ?, ?)

        ON CONFLICT(job_id, country, observed_date)
        DO UPDATE SET
            skill_hash = excluded.skill_hash,
            skills_snapshot = excluded.skills_snapshot
    """, (
        job_id,
        country,
        observed_date,
        skills_hash,
        skills_json
    ))

def sync_job_skills(conn, job_id, skills, imported_at):
    skills = set(skills)

    for skill_name in skills:
        conn.execute("""
            INSERT INTO skill (name, first_seen_at)
            VALUES (?, ?)
            ON CONFLICT(name) DO NOTHING
        """, (skill_name, imported_at))

    # Удаляем старые связи только для этой вакансии
    conn.execute("""
        DELETE FROM job_skill
        WHERE job_id = ?
    """, (job_id,))

    for skill_name in skills:
        conn.execute("""
            INSERT INTO job_skill (job_id, skill_id)
            SELECT ?, skill_id
            FROM skill
            WHERE name = ?
        """, (job_id, skill_name))

def load_meetfrank():
    create_tables()

    with open(DATA_FILE, encoding="utf-8") as file:
        data = json.load(file)

    jobs = data["jobs"] if isinstance(data, dict) else data

    # Время импорта, а не дата первого появления вакансии в API
    imported_at = datetime.now(timezone.utc).isoformat()

    with closing(get_connection()) as conn:
        with conn:
            for job in jobs:
                job_id = str(job["id"])
                country = job["country"]
                skills = set(job.get("skills") or [])

                # 1. Сохраняем уникальную вакансию
                conn.execute("""
                    INSERT INTO job (
                        job_id, title, company, location,
                        remote_type, speciality, seniorities,
                        employment_type, published_at, apply_url,
                        first_seen_at, last_seen_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

                    ON CONFLICT(job_id) DO UPDATE SET
                        title = excluded.title,
                        company = excluded.company,
                        location = excluded.location,
                        remote_type = excluded.remote_type,
                        speciality = excluded.speciality,
                        seniorities = excluded.seniorities,
                        employment_type = excluded.employment_type,
                        published_at = excluded.published_at,
                        apply_url = excluded.apply_url
                """, (
                    job_id,
                    job.get("title"),
                    job.get("company"),
                    job.get("location"),
                    job.get("remote_type"),
                    job.get("speciality"),
                    json.dumps(job.get("seniorities"), ensure_ascii=False),
                    job.get("employment_type"),
                    job.get("published_at"),
                    job.get("apply_url"),
                    imported_at,
                    imported_at
                ))

                # 2. Сохраняем связь вакансии со страной
                conn.execute("""
                    INSERT INTO job_countries (
                        job_id, country, first_seen_at, last_seen_at
                    )
                    VALUES (?, ?, ?, ?)

                    ON CONFLICT(job_id, country) DO NOTHING
                """, (job_id, country, imported_at, imported_at))

                # 3. Сохраняем навыки и связи с вакансией
                for skill_name in skills:
                    conn.execute("""
                        INSERT INTO skill (name, first_seen_at)
                        VALUES (?, ?)
                        ON CONFLICT(name) DO NOTHING
                    """, (skill_name, imported_at))

                    skill_id = conn.execute("""
                        SELECT skill_id
                        FROM skill
                        WHERE name = ?
                    """, (skill_name,)).fetchone()[0]

                    conn.execute("""
                        INSERT INTO job_skill (job_id, skill_id)
                        VALUES (?, ?)
                        ON CONFLICT(job_id, skill_id) DO NOTHING
                    """, (job_id, skill_id))

    print("\nMeetFrank data loaded successfully.")

    with closing(get_connection()) as conn:
        with conn:
            for table in ("job", "job_countries", "skill", "job_skill"):
                count = conn.execute(
                    f"SELECT COUNT(*) FROM {table}"
                ).fetchone()[0]

                print(f"{table}: {count}")


if __name__ == "__main__":
    load_meetfrank()
