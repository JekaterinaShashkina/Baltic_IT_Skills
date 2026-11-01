
from contextlib import closing
import sqlite3
import time
from datetime import datetime, timezone

from ..config import DB_PATH, ESCO_VERSION
from ..logger import get_logger
from .fetch_esco import search_esco_skill, get_esco_skill_details


logger = get_logger(__name__)


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
    """Classify the match between MeetFrank and ESCO skill names."""

    meetfrank_name = skill_name.strip().casefold()
    esco_name = esco_title.strip().casefold()

    if meetfrank_name == esco_name:
        return "exact"

    if alternative_labels:
        for label in alternative_labels:
            if meetfrank_name == label.strip().casefold():

                # Do not classify a broad concept as an exact match.
                if esco_name == "computer programming":
                    return "review"

                return "exact"

    return "review"

def save_esco_mapping(skill_name, esco_title, esco_uri, mapping_method="manual"):
    """Save a confirmed mapping between a MeetFrank skill and ESCO."""

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
                (esco_uri, esco_title, ESCO_VERSION, now)
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
    """Save the result of an ESCO skill check."""

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
                ESCO_VERSION,
                skill_name
            ))


def check_esco_matches(limit=20):
    """Match new MeetFrank skills against ESCO."""

    skills = get_skills(limit=limit)

    stats = {
        "checked": 0,
        "matched": 0,
        "no_match": 0,
        "failed": 0
    }

    logger.info(
        "ESCO matching started. Skills to check: %s",
        len(skills),
    )

    for skill_name in skills:
        logger.info("Checking ESCO skill: %s", skill_name)

        try:
            data = search_esco_skill(skill_name)
            results = data.get("_embedded", {}).get("results", [])

            match = find_exact_match(skill_name, results)

            if match:
                save_esco_mapping(
                    skill_name,
                    match["title"],
                    match["uri"],
                    mapping_method="automatic"
                )

                save_esco_check(skill_name, "exact")
                stats["matched"] += 1
                logger.info(
                    "Exact ESCO match: %s -> %s",
                    skill_name,
                    match["title"],
                )
            else:
                save_esco_check(skill_name, "no_match")
                stats["no_match"] += 1
                logger.info(
                    "No exact ESCO match found for: %s",
                    skill_name,
                )

            stats["checked"] += 1

        except Exception:
            stats["failed"] += 1
            logger.exception(
                "ESCO processing failed for skill: %s",
                skill_name,
            )

        time.sleep(1)
    logger.info(
        "ESCO matching batch completed. Checked: %s, matched: %s, "
        "no match: %s, failed: %s",
        stats["checked"],
        stats["matched"],
        stats["no_match"],
        stats["failed"],
    )

    return stats


if __name__ == "__main__":
    from ..logger import setup_logging

    setup_logging()
    check_esco_matches()

    total, mapped = get_skill_statistics()

    logger.info("Total MeetFrank skills: %s", total)
    logger.info("Exact ESCO mappings: %s", mapped)
    logger.info("Skills without exact mapping: %s", total - mapped)

