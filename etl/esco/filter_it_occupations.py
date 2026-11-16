import time
from contextlib import closing
from datetime import datetime, timezone
import re

import requests

from ..config import (
    ESCO_LANGUAGE,
    ESCO_OCCUPATION_URL,
    ESCO_VERSION,
    REQUEST_TIMEOUT,
)
from ..database import get_connection
from ..logger import get_logger, setup_logging

logger = get_logger(__name__)

EXTRA_ICT_CODES = {
    "1330.6",  # ICT product manager
    "1330.7",  # ICT project manager
}

def is_ict_occupation(code):
    return (
        code.startswith(("25", "35"))
        or code in EXTRA_ICT_CODES
    )


def validate_occupation_code(code):
    """Validate an ESCO occupation code."""

    if not isinstance(code, str):
        raise ValueError("Occupation code must be a string")

    code = code.strip()

    if not re.fullmatch(r"\d{4}(?:\.\d+)*", code):
        raise ValueError(f"Invalid occupation code: {code}")

    return code


def get_pending_occupations(limit=20):
    """Return occupations that have not been classified yet."""

    with closing(get_connection()) as conn:
        rows = conn.execute(
            """
            SELECT occupation_uri, title
            FROM occupation
            WHERE fetched_at IS NULL
            ORDER BY occupation_uri
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    return rows


def save_occupation_classification(occupation_uri, code):
    """Save an occupation code and its ICT classification."""

    category = "ICT" if is_ict_occupation(code) else "non-ICT"

    with closing(get_connection()) as conn:
        with conn:
            cursor = conn.execute(
                """
                UPDATE occupation
                SET
                    isco_code = ?,
                    ict_category = ?,
                    fetched_at = ?
                WHERE occupation_uri = ?
                """,
                (
                    code,
                    category,
                    datetime.now(timezone.utc).isoformat(),
                    occupation_uri,
                ),
            )

            if cursor.rowcount != 1:
                raise ValueError(
                    f"Occupation not found: {occupation_uri}"
                )

    return category


def filter_it_occupations(limit=20):
    """Fetch occupation codes and classify occupations as ICT or non-ICT."""

    occupations = get_pending_occupations(limit=limit)

    logger.info(
        "Starting ESCO occupation classification. Pending: %s",
        len(occupations),
    )

    stats = {
        "processed": 0,
        "ict": 0,
        "non_ict": 0,
        "failed": 0,
    }

    for number, (uri, title) in enumerate(occupations, start=1):
        logger.info(
            "Classifying occupation %s/%s: %s",
            number,
            len(occupations),
            title,
        )

        try:
            response = requests.get(
                ESCO_OCCUPATION_URL,
                params={
                    "uri": uri,
                    "language": ESCO_LANGUAGE,
                    "selectedVersion": ESCO_VERSION,
                },
                timeout=REQUEST_TIMEOUT,
            )
            response.raise_for_status()

            data = response.json()

            if not isinstance(data, dict):
                raise ValueError("Invalid ESCO occupation response")

            code = data.get("code")

            if not isinstance(code, str) or not code.strip():
                raise ValueError(
                    f"Missing occupation code for {uri}"
                )

            code = validate_occupation_code(code)

            category = save_occupation_classification(uri, code)

            stats["processed"] += 1

            if category == "ICT":
                stats["ict"] += 1
            else:
                stats["non_ict"] += 1

            logger.info("%s: %s (%s)", title, code, category)

        except (requests.RequestException, ValueError):
            stats["failed"] += 1
            logger.exception(
                "Failed to classify occupation: %s",
                title,
            )

        time.sleep(0.2)

    logger.info(
        "ESCO occupation classification completed: %s",
        stats,
    )

    return stats


if __name__ == "__main__":
    setup_logging()
    filter_it_occupations()
