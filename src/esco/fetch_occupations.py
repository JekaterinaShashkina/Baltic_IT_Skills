import json
import time
from pathlib import Path

import requests

from ..config import ESCO_SKILL_URL, ESCO_VERSION, REQUEST_TIMEOUT

BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = BASE_DIR / "data" / "processed" / "esco_skill_mapping.json"
OUTPUT_FILE = BASE_DIR / "data" / "processed" / "esco_skill_occupations.json"

def fetch_occupations():
    # Load confirmed ESCO skill mappings
    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        mapping = json.load(file)

    # Collect unique ESCO skill URIs
    # Multiple MeetFrank skills may map to the same ESCO skill
    unique_uris = {
        info["esco_uri"]
        for info in mapping.values()
        if info["status"] in ("exact", "broader")
        and info.get("esco_uri")
    }

    print(f"Unique ESCO skills: {len(unique_uris)}")

    occupations_data = {}

    for number, uri in enumerate(sorted(unique_uris), start=1):
        print(f"[{number}/{len(unique_uris)}] {uri}")

        try:
            response = requests.get(
                ESCO_SKILL_URL,
                params={
                    "uri": uri,
                    "language": "en",
                    "selectedVersion": ESCO_VERSION
                },
                timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()

            data = response.json()
            links = data.get("_links", {})

            essential = links.get("isEssentialForOccupation", [])
            optional = links.get("isOptionalForOccupation", [])

            # Handle API responses containing a single object instead of a list
            if isinstance(essential, dict):
                essential = [essential]

            if isinstance(optional, dict):
                optional = [optional]

            occupations_data[uri] = {
                "esco_title": data.get("title"),
                "essential_occupations": [
                    {
                        "title": item.get("title"),
                        "uri": item.get("uri")
                    }
                    for item in essential
                ],
                "optional_occupations": [
                    {
                        "title": item.get("title"),
                        "uri": item.get("uri")
                    }
                    for item in optional
                ]
            }

        except (requests.RequestException, ValueError) as error:
            print(f"ERROR: {error}")
            occupations_data[uri] = {
                "error": str(error)
            }

        time.sleep(0.2)

    # Save occupation relationships
    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(occupations_data, file, ensure_ascii=False, indent=4)

    print("\nFinished.")
    print(f"ESCO skills processed: {len(occupations_data)}")
    print(f"Saved: {OUTPUT_FILE}")

if __name__ == "__main__":
    fetch_occupations()   