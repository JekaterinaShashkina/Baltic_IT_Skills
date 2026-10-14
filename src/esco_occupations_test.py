import json
import time
from pathlib import Path

import requests

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "data" / "processed" / "esco_skill_mapping.json"
OUTPUT_FILE = BASE_DIR / "data" / "processed" / "esco_skill_occupations.json"

ESCO_URL = "https://ec.europa.eu/esco/api/resource/skill"

# Загружаем подтверждённые соответствия
with open(INPUT_FILE, "r", encoding="utf-8") as file:
    mapping = json.load(file)

# Собираем уникальные ESCO URI
# Несколько MeetFrank skills могут ссылаться на один ESCO skill
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
            ESCO_URL,
            params={
                "uri": uri,
                "language": "en",
                "selectedVersion": "v1.2.0"
            },
            timeout=30
        )
        response.raise_for_status()

        data = response.json()
        links = data.get("_links", {})

        essential = links.get("isEssentialForOccupation", [])
        optional = links.get("isOptionalForOccupation", [])

        # На случай, если API вернёт один объект вместо списка
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

# Сохраняем результат
with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
    json.dump(occupations_data, file, ensure_ascii=False, indent=4)

print("\nFinished.")
print(f"ESCO skills processed: {len(occupations_data)}")
print(f"Saved: {OUTPUT_FILE}")