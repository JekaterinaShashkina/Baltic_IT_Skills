
import json
from datetime import datetime, timezone
from contextlib import closing

from ..database import get_connection
from ..logger import get_logger
from .observations import save_observation
from .job_skills import sync_job_skills


logger = get_logger(__name__)


def update_meetfrank(jobs, observed_at=None, run_id=None):
    if observed_at is None:
        observed_at = datetime.now(timezone.utc)

    timestamp = observed_at.isoformat()
    observed_date = observed_at.date().isoformat()

    logger.info(
        "Updating MeetFrank database. Country records: %s, observation date: %s",
        len(jobs),
        observed_date,
    )

    # Group jobs by ID because the same job may appear in multiple countries.
    grouped = {}

    for job in jobs:
        job_id = str(job["id"])
        country = job["country"]
        skills = set(job.get("skills") or [])

        if job_id not in grouped:
            grouped[job_id] = {
                "job": job,
                "skills": skills,
                "countries": set()
            }
        elif grouped[job_id]["skills"] != skills:
            raise ValueError(
                f"Different skills for job {job_id} across countries"
            )

        if country in grouped[job_id]["countries"]:
            raise ValueError(
                f"Duplicate job-country pair: {job_id}, {country}"
            )

        grouped[job_id]["countries"].add(country)

    # Perform all database changes within a single transaction.
    with closing(get_connection()) as conn:
        with conn:
            existing_job_ids = {
                row[0]
                for row in conn.execute("SELECT job_id FROM job")
            }

            new_jobs = sum(
                1 for job_id in grouped
                if job_id not in existing_job_ids
            )

            updated_jobs = len(grouped) - new_jobs
            existing_skills = {
                row[0]
                for row in conn.execute("SELECT name FROM skill")
            }

            incoming_skills = set()

            for item in grouped.values():
                incoming_skills.update(item["skills"])

            new_skills = len(incoming_skills - existing_skills)

            for job_id, item in grouped.items():
                job = item["job"]
                skills = item["skills"]

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
                        apply_url = excluded.apply_url,
                        last_seen_at = excluded.last_seen_at
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
                    timestamp,
                    timestamp
                ))

                sync_job_skills(conn, job_id, skills, timestamp)

                for country in item["countries"]:
                    conn.execute("""
                        INSERT INTO job_countries (
                            job_id, country, first_seen_at, last_seen_at
                        )
                        VALUES (?, ?, ?, ?)
                        ON CONFLICT(job_id, country) DO UPDATE SET
                            last_seen_at = excluded.last_seen_at
                    """, (job_id, country, timestamp, timestamp))

                    save_observation(
                        conn, job_id, country, skills, observed_date, run_id=run_id
                    )

    logger.info(
        "MeetFrank database updated. Date: %s, unique jobs: %s, "
        "country records: %s, new jobs: %s, updated jobs: %s, new skills: %s",
        observed_date,
        len(grouped),
        len(jobs),
        new_jobs,
        updated_jobs,
        new_skills,
    )

    return {
        "new_jobs": new_jobs,
        "updated_jobs": updated_jobs,
        "new_skills": new_skills,
    }