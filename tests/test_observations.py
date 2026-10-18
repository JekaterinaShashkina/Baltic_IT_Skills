
import sqlite3
import json
from src.load_meetfrank import save_observation, sync_job_skills

# Временная база существует только во время теста
conn = sqlite3.connect(":memory:")
conn.execute("PRAGMA foreign_keys = ON")

# Создаём минимальные таблицы для проверки
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

conn.execute("INSERT INTO job VALUES ('1001')")
conn.execute(
    "INSERT INTO job_countries VALUES ('1001', 'estonia')"
)

# День 1: Python + Docker
sync_job_skills(conn, "1001", ["Python", "Docker"], "2026-10-12")
save_observation(
    conn, "1001", "estonia",
    ["Python", "Docker"], "2026-10-12"
)

# День 2: навыки не изменились
sync_job_skills(conn, "1001", ["Python", "Docker"], "2026-10-13")
save_observation(
    conn, "1001", "estonia",
    ["Python", "Docker"], "2026-10-13"
)

# День 3: Docker заменили на Kubernetes
sync_job_skills(conn, "1001", ["Python", "Kubernetes"], "2026-10-14")
save_observation(
    conn, "1001", "estonia",
    ["Python", "Kubernetes"], "2026-10-14"
)

# Повторно записываем день 3
save_observation(
    conn, "1001", "estonia",
    ["Python", "Kubernetes"], "2026-10-14"
)

# Проверяем актуальные навыки
current = [
    row[0] for row in conn.execute("""
        SELECT s.name
        FROM job_skill js
        JOIN skill s ON s.skill_id = js.skill_id
        ORDER BY s.name
    """)
]

# Проверяем историю
history = [
    (day, json.loads(snapshot))
    for day, snapshot in conn.execute("""
        SELECT observed_date, skills_snapshot
        FROM job_observation
        ORDER BY observed_date
    """)
]

print("CURRENT SKILLS:", current)
print("HISTORY:")
for day, skills in history:
    print(day, skills)

assert current == ["Kubernetes", "Python"]
assert len(history) == 3
assert history[0][1] == ["Docker", "Python"]
assert history[2][1] == ["Kubernetes", "Python"]

print("ALL TESTS PASSED")
conn.close()
