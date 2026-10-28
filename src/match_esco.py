
from contextlib import closing
import sqlite3
import time

from src.database import DB_PATH
from src.fetch_esco import search_esco_skill, get_esco_skill_details
from datetime import datetime, timezone


def get_skills(limit=5):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        rows = conn.execute("""
            SELECT s.name
            FROM skill s
            WHERE NOT EXISTS (
                SELECT 1
                FROM skill_mapping m
                WHERE m.skill_id = s.skill_id
            )
            AND NOT EXISTS (
                SELECT 1
                FROM esco_check ec
                WHERE ec.skill_id = s.skill_id
            )
            ORDER BY s.skill_id
            LIMIT ?
        """, (limit,)).fetchall()

    return [row[0] for row in rows]

def classify_match(skill_name, esco_title, alternative_labels=None):
    """Проверяет совпадение названий навыков MeetFrank и ESCO."""

    meetfrank_name = skill_name.strip().casefold()
    esco_name = esco_title.strip().casefold()

    if meetfrank_name == esco_name:
        return "exact"

    if alternative_labels:
        for label in alternative_labels:
            if meetfrank_name == label.strip().casefold():

                # Не считаем совпадение с широким понятием точным
                if esco_name == "computer programming":
                    return "review"

                return "exact"

    return "review"

def save_esco_mapping(skill_name, esco_title, esco_uri, mapping_method="manual"):
    """Сохраняет проверенное соответствие MeetFrank и ESCO."""

    now = datetime.now(timezone.utc).isoformat()

    with closing(sqlite3.connect(DB_PATH)) as conn:
        with conn:
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
                VALUES (?, ?, 'exact', ?, ?)
                ON CONFLICT(skill_id) DO NOTHING
                """,
                (skill_id, esco_uri, mapping_method, now)
            )

def find_exact_match(skill_name, results):
    for result in results:
        esco_uri = result.get("uri")
        if not esco_uri:
            continue

        details = get_esco_skill_details(esco_uri)

        preferred_label = details.get("preferredLabel", {}).get("en", "")
        alternative_labels = details.get("alternativeLabel", {}).get("en", [])

        status = classify_match(
            skill_name,
            preferred_label,
            alternative_labels
        )

        if status == "exact":
            return {
                "title": preferred_label,
                "uri": esco_uri,
                "status": status
            }

    return None

def get_skill_statistics():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        total = conn.execute(
            "SELECT COUNT(*) FROM skill"
        ).fetchone()[0]

        mapped = conn.execute(
            "SELECT COUNT(*) FROM skill_mapping WHERE status = 'exact'"
        ).fetchone()[0]

    return total, mapped

def save_esco_check(skill_name, status):
    """Сохраняет результат проверки навыка через ESCO."""

    now = datetime.now(timezone.utc).isoformat()

    with closing(sqlite3.connect(DB_PATH)) as conn:
        with conn:
            conn.execute("""
                INSERT INTO esco_check (
                    skill_id, status, checked_at, esco_version
                )
                SELECT skill_id, ?, ?, ?
                FROM skill
                WHERE name = ?
                ON CONFLICT(skill_id) DO UPDATE SET
                    status = excluded.status,
                    checked_at = excluded.checked_at,
                    esco_version = excluded.esco_version
            """, (
                status,
                now,
                "v1.2.0",
                skill_name
            ))


def check_esco_matches():
    """Ищет соответствия навыков в ESCO."""

    skills = get_skills(limit=20)

    for skill_name in skills:
        print(f"\nMeetFrank skill: {skill_name}")

        try:
            data = search_esco_skill(skill_name)
            results = data.get("_embedded", {}).get("results", [])

            match = find_exact_match(skill_name, results)

            if match:
                print("  Exact ESCO match:", match["title"])
                print("  ESCO URI:", match["uri"])

                save_esco_mapping(
                    skill_name,
                    match["title"],
                    match["uri"],
                    mapping_method="automatic"
                )

                save_esco_check(skill_name, "exact")

                print("  Mapping saved to SQLite")
            else:
                save_esco_check(skill_name, "no_match")

                print("  No exact ESCO match")
        except Exception as error:
            print(f"  ESCO request failed: {error}")

        time.sleep(1)


if __name__ == "__main__":
    while True:
        remaining_skills = get_skills(limit=20)

        if not remaining_skills:
            break

        check_esco_matches()

    total, mapped = get_skill_statistics()

    print("\n=== ESCO MATCHING COMPLETED ===")
    print(f"Total MeetFrank skills: {total}")
    print(f"Exact ESCO mappings: {mapped}")
    print(f"Skills without exact mapping: {total - mapped}")

