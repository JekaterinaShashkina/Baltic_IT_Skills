import time
from contextlib import closing
from datetime import datetime, timezone

import requests

from ..config import ESCO_LANGUAGE, ESCO_SKILL_URL, ESCO_VERSION, REQUEST_TIMEOUT
from ..database import get_connection
from ..logger import get_logger

logger = get_logger(__name__)


def get_mapped_esco_skills(limit=20):
    """Return unique ESCO skill URIs with confirmed mappings."""

    with closing(get_connection()) as conn:
        rows = conn.execute(
            """
            SELECT DISTINCT sm.esco_uri
            FROM skill_mapping AS sm
            LEFT JOIN esco_occupation_fetch AS eof
                ON sm.esco_uri = eof.esco_uri
            WHERE sm.status IN ('exact', 'broader')
            AND sm.esco_uri IS NOT NULL
            AND eof.esco_uri IS NULL
            ORDER BY sm.esco_uri
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    return [row[0] for row in rows]


def check_occupation_conflicts(data):
    """Reject occupations with conflicting relationship types."""

    links = data.get("_links", {})

    def extract_uris(relation_name):
        occupations = links.get(relation_name, [])

        if isinstance(occupations, dict):
            occupations = [occupations]

        return {
            occupation["uri"]
            for occupation in occupations
        }

    essential_uris = extract_uris("isEssentialForOccupation")
    optional_uris = extract_uris("isOptionalForOccupation")

    conflicts = essential_uris & optional_uris

    if conflicts:
        raise ValueError(
            "Conflicting ESCO occupation relationships: "
            + ", ".join(sorted(conflicts))
        )


def save_skill_occupations(esco_uri, data):
    """Save ESCO occupations and their relationships to a skill."""

    validate_occupation_response(data)
    check_occupation_conflicts(data)

    links = data.get("_links", {})

    relation_types = {
        "isEssentialForOccupation": "essential",
        "isOptionalForOccupation": "optional",
    }

    saved_relations = 0

    with closing(get_connection()) as conn:
        with conn:
            for link_name, relation_type in relation_types.items():
                occupations = links.get(link_name, [])

                if isinstance(occupations, dict):
                    occupations = [occupations]

                for occupation in occupations:
                    occupation_uri = occupation.get("uri")
                    title = occupation.get("title")

                    if not occupation_uri or not title:
                        logger.warning(
                            "Skipping occupation with missing URI or title: %s",
                            occupation,
                        )
                        continue

                    conn.execute(
                        """
                        INSERT INTO occupation (occupation_uri, title)
                        VALUES (?, ?)
                        ON CONFLICT(occupation_uri) DO UPDATE SET
                            title = excluded.title
                        """,
                        (occupation_uri, title),
                    )

                    conn.execute(
                        """
                        INSERT INTO esco_skill_occupation (
                            esco_uri,
                            occupation_uri,
                            relation_type
                        )
                        VALUES (?, ?, ?)
                        ON CONFLICT(esco_uri, occupation_uri) DO UPDATE SET
                            relation_type = excluded.relation_type
                        """,
                        (esco_uri, occupation_uri, relation_type),
                    )

                    saved_relations += 1
            
            conn.execute(
                """
                INSERT INTO esco_occupation_fetch (
                    esco_uri,
                    fetched_at,
                    relation_count
                )
                VALUES (?, ?, ?)
                ON CONFLICT(esco_uri) DO UPDATE SET
                    fetched_at = excluded.fetched_at,
                    relation_count = excluded.relation_count
                """,
                (
                    esco_uri,
                    datetime.now(timezone.utc).isoformat(),
                    saved_relations,
                ),
            )

    logger.info(
        "Saved %s occupation relationships for ESCO skill %s",
        saved_relations,
        esco_uri,
    )

    return saved_relations


def validate_occupation_response(data):
    """Validate the ESCO skill response before saving occupations."""

    if not isinstance(data, dict):
        raise ValueError("ESCO response must be a JSON object")

    links = data.get("_links")

    if not isinstance(links, dict):
        raise ValueError("ESCO response has no valid _links object")

    for relation_name in (
        "isEssentialForOccupation",
        "isOptionalForOccupation",
    ):
        occupations = links.get(relation_name, [])

        if not isinstance(occupations, (list, dict)):
            raise ValueError(
                f"Invalid occupation relationship: {relation_name}"
            )

        if isinstance(occupations, dict):
            occupations = [occupations]

        for occupation in occupations:
            if not isinstance(occupation, dict):
                raise ValueError(
                    f"Invalid occupation entry in {relation_name}"
                )

            if not occupation.get("uri") or not occupation.get("title"):
                raise ValueError(
                    f"Occupation is missing URI or title in {relation_name}"
                )


def fetch_occupations(limit=20):
    """Fetch and save occupations for unmapped ESCO skill relations."""

    skills = get_mapped_esco_skills(limit=limit)

    logger.info(
        "Starting ESCO occupation fetching. Skills to process: %s",
        len(skills),
    )

    stats = {
        "processed": 0,
        "relations": 0,
        "failed": 0,
        "skipped": 0,
    }

    for number, esco_uri in enumerate(skills, start=1):
        logger.info(
            "Processing ESCO skill %s/%s: %s",
            number,
            len(skills),
            esco_uri,
        )

        try:
            response = requests.get(
                ESCO_SKILL_URL,
                params={
                    "uri": esco_uri,
                    "language": ESCO_LANGUAGE,
                    "selectedVersion": ESCO_VERSION,
                },
                timeout=REQUEST_TIMEOUT,
            )

            response.raise_for_status()

            data = response.json()
            validate_occupation_response(data)

            links = data["_links"]

            if not any(
                key in links
                for key in (
                    "isEssentialForOccupation",
                    "isOptionalForOccupation",
                )
            ):
                logger.warning(
                    "No occupation relationship fields for %s. "
                    "Skipping until the response can be verified.",
                    esco_uri,
                )
                stats["skipped"] += 1
                continue

            relation_count = save_skill_occupations(
                esco_uri,
                data,
            )

            stats["processed"] += 1
            stats["relations"] += relation_count

        except (requests.RequestException, ValueError) as error:
            stats["failed"] += 1
            logger.exception(
                "Failed to fetch occupations for ESCO skill %s",
                esco_uri,
            )

        time.sleep(0.2)

    logger.info(
        "ESCO occupation fetching completed. Statistics: %s",
        stats,
    )

    return stats


if __name__ == "__main__":
    from ..logger import setup_logging

    setup_logging()
    fetch_occupations()