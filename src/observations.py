
import hashlib
import json


def save_observation(conn, job_id, country, skills, observed_date, run_id=None):
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
            skill_hash, skills_snapshot, run_id
        )
        VALUES (?, ?, ?, ?, ?, ?)

        ON CONFLICT(job_id, country, observed_date)
        DO UPDATE SET
            skill_hash = excluded.skill_hash,
            skills_snapshot = excluded.skills_snapshot,
            run_id = excluded.run_id
    """, (
        job_id,
        country,
        observed_date,
        skills_hash,
        skills_json,
        run_id
    ))
