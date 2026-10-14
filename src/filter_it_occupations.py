import json
import time
from pathlib import Path

import requests

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "processed"

INPUT_FILE = DATA_DIR / "esco_skill_occupations.json"
OUTPUT_FILE = DATA_DIR / "esco_it_occupations.json"

ESCO_URL = "https://ec.europa.eu/esco/api/resource/occupation"

EXTRA_ICT_CODES = {
    "1330.6",  # ICT product manager
    "1330.7",  # ICT project manager
}

def is_ict_occupation(code):
    return (
        code.startswith(("25", "35"))
        or code in EXTRA_ICT_CODES
    )

with open(INPUT_FILE, encoding="utf-8") as file:
    skills_data = json.load(file)

# Собираем уникальные профессии
unique_occupations = {}

for skill_data in skills_data.values():
    for relation in ("essential_occupations", "optional_occupations"):
        for occupation in skill_data.get(relation, []):
            uri = occupation.get("uri")
            if uri:
                unique_occupations[uri] = occupation["title"]

print(f"Unique occupations: {len(unique_occupations)}")

# Получаем ISCO-коды
occupation_codes = {}

for number, (uri, title) in enumerate(unique_occupations.items(), start=1):
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
        code = str(data.get("code", ""))

        occupation_codes[uri] = {
            "title": title,
            "code": code,
            "is_it": is_ict_occupation(code)
        }

        print(f"[{number}/{len(unique_occupations)}] {title}: {code}")

    except (requests.RequestException, ValueError) as error:
        print(f"ERROR: {title}: {error}")
        occupation_codes[uri] = {
            "title": title,
            "code": None,
            "is_it": False,
            "error": str(error)
        }

    time.sleep(0.2)

CODES_FILE = DATA_DIR / "esco_occupation_codes.json"

with open(CODES_FILE, "w", encoding="utf-8") as file:
    json.dump(occupation_codes, file, ensure_ascii=False, indent=4)

# Фильтруем связи навыков с профессиями
filtered_data = {}

for skill_uri, skill_data in skills_data.items():
    filtered_data[skill_uri] = {
        "esco_title": skill_data.get("esco_title"),
        "essential_occupations": [],
        "optional_occupations": []
    }

    for relation in ("essential_occupations", "optional_occupations"):
        for occupation in skill_data.get(relation, []):
            uri = occupation["uri"]

            if occupation_codes.get(uri, {}).get("is_it"):
                filtered_data[skill_uri][relation].append({
                    **occupation,
                    "isco_code": occupation_codes[uri]["code"]
                })

# Сохраняем результаты
with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
    json.dump(filtered_data, file, ensure_ascii=False, indent=4)

print("\nFinished.")
print(f"IT occupations: {sum(x['is_it'] for x in occupation_codes.values())}")
print(f"Saved: {OUTPUT_FILE}")


