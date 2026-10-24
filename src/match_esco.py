
import sqlite3
import time

from src.database import DB_PATH
from src.fetch_esco import search_esco_skill
from datetime import datetime, timezone


def get_skills(limit=5):
    """Получает навыки, ещё не сопоставленные с ESCO."""

    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            """
            SELECT s.name
            FROM skill s
            WHERE NOT EXISTS (
                SELECT 1
                FROM skill_mapping m
                WHERE m.skill_id = s.skill_id
            )
            ORDER BY s.skill_id
            LIMIT ?
            """,
            (limit,)
        ).fetchall()

    return [row[0] for row in rows]


def classify_match(skill_name, esco_title):
    """Проверяет точное совпадение названий навыков."""

    meetfrank_name = skill_name.strip().casefold()
    esco_name = esco_title.strip().casefold()

    # Полностью одинаковые названия
    if meetfrank_name == esco_name:
        return "exact"

    # Название ESCO с уточнением в скобках
    if esco_name.startswith(meetfrank_name + " ("):
        return "exact"

    return "review"

def save_esco_mapping(skill_name, esco_title, esco_uri):
    """Сохраняет проверенное соответствие MeetFrank и ESCO."""

    now = datetime.now(timezone.utc).isoformat()

    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(
            "SELECT skill_id FROM skill WHERE name = ?",
            (skill_name,)
        ).fetchone()

        if row is None:
            raise ValueError(f"Skill not found: {skill_name}")

        skill_id = row[0]

        conn.execute(
            """
            INSERT OR IGNORE INTO esco_skill
                (esco_uri, title, version, fetched_at)
            VALUES (?, ?, ?, ?)
            """,
            (esco_uri, esco_title, "v1.2.0", now)
        )

        conn.execute(
            """
            INSERT INTO skill_mapping
                (skill_id, esco_uri, status,
                mapping_method, reviewed_at)
            VALUES (?, ?, 'exact', 'manual', ?)
            ON CONFLICT(skill_id) DO UPDATE SET
                esco_uri = excluded.esco_uri,
                status = excluded.status,
                mapping_method = excluded.mapping_method,
                reviewed_at = excluded.reviewed_at
            """,
            (skill_id, esco_uri, now)
        )



def check_esco_matches():
    """Ищет соответствия навыков в ESCO."""

    skills = get_skills()

    for skill_name in skills:
        print(f"\nMeetFrank skill: {skill_name}")

        try:
            data = search_esco_skill(skill_name)

            results = data.get("_embedded", {}).get("results", [])

            if not results:
                print("  No ESCO matches found")

            for result in results[:3]:
                esco_title = result.get("title", "")
                esco_uri = result.get("uri")

                status = classify_match(skill_name, esco_title)

                print("  ESCO title:", esco_title)
                print("  ESCO URI:", esco_uri)
                print("  Status:", status)
                print("  ---")

        except Exception as error:
            print(f"  ESCO request failed: {error}")

        time.sleep(1)


if __name__ == "__main__":
        skills = get_skills()

        print("Unmapped skills:")
        for skill in skills:
            print("-", skill)
