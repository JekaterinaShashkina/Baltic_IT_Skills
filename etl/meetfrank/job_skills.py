
def sync_job_skills(conn, job_id, skills, imported_at):
    skills = set(skills)

    for skill_name in skills:
        conn.execute("""
            INSERT INTO skill (name, first_seen_at)
            VALUES (?, ?)
            ON CONFLICT(name) DO NOTHING
        """, (skill_name, imported_at))

    # Remove existing skill associations only for this job
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
