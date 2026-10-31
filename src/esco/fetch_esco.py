import requests

from ..config import (
    ESCO_API_URL,
    ESCO_SKILL_URL,
    ESCO_VERSION,
    ESCO_LANGUAGE,
    ESCO_SEARCH_LIMIT,
    REQUEST_TIMEOUT,
)
from ..logger import get_logger

logger = get_logger(__name__)


def search_esco_skill(skill_name):
    logger.debug("Searching ESCO for skill: %s", skill_name)
    params = {
        "text": skill_name,
        "language": ESCO_LANGUAGE,
        "type": "skill",
        "limit": ESCO_SEARCH_LIMIT,
        "selectedVersion": ESCO_VERSION
    }

    response = requests.get(
        ESCO_API_URL,
        params=params,
        timeout=REQUEST_TIMEOUT
    )

    response.raise_for_status()

    content_type = response.headers.get("Content-Type", "")

    if "application/json" not in content_type.lower():
        raise ValueError(
            f"ESCO API returned unexpected content: "
            f"HTTP {response.status_code}, "
            f"Content-Type: {content_type}"
        )
    
    logger.debug(
        "ESCO search response received for skill: %s",
        skill_name,
    )
    return response.json()


def get_esco_skill_details(esco_uri):

    params = {
        "uri": esco_uri,
        "language": ESCO_LANGUAGE,
        "selectedVersion": ESCO_VERSION
    }

    logger.debug("Fetching ESCO skill details: %s", esco_uri)

    response = requests.get(
        ESCO_SKILL_URL, 
        params=params, 
        timeout=REQUEST_TIMEOUT)
    
    response.raise_for_status()

    content_type = response.headers.get("Content-Type", "")

    if "application/json" not in content_type.lower():
        raise ValueError(
            f"ESCO API returned unexpected content: "
            f"HTTP {response.status_code}, "
            f"Content-Type: {content_type}"
        )
    
    logger.debug("ESCO skill details received: %s", esco_uri)

    return response.json()

