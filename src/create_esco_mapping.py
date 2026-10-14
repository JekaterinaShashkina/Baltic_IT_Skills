import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "data" / "processed" / "esco_skill_mapping_candidates.json"
OUTPUT_FILE = BASE_DIR / "data" / "processed" / "esco_skill_mapping.json"

MANUAL_FILE = BASE_DIR / "data" / "processed" / "manual_esco_mapping.json"

with open(INPUT_FILE, "r", encoding="utf-8") as file:
    data = json.load(file)

with open(MANUAL_FILE, "r", encoding="utf-8") as file:
    manual_mapping = json.load(file)

mapping = {}

for skill, info in data.items():
    candidates = info.get("candidates", [])

    # Сначала ищем точное совпадение названий
    exact_match = None

    for candidate in candidates:
        title = candidate.get("title") or ""

        if skill.strip().casefold() == title.strip().casefold():
            exact_match = candidate
            break

    if exact_match:
        status = "exact"
        selected = exact_match
    else:
        status = "review"
        selected = None

    # Ручные решения имеют приоритет
    if skill in manual_mapping:
        manual = manual_mapping[skill]

        status = manual["status"]
        esco_title = manual["esco_title"]
        esco_uri = manual["esco_uri"]
    else:
        esco_title = selected["title"] if selected else None
        esco_uri = selected["uri"] if selected else None

    mapping[skill] = {
        "meetfrank_frequency": info["meetfrank_frequency"],
        "status": status,
        "esco_title": esco_title,
        "esco_uri": esco_uri,
        "candidates": candidates
    }

with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
    json.dump(mapping, file, ensure_ascii=False, indent=4)

from collections import Counter

status_counts = Counter(
    item["status"] for item in mapping.values()
)

print(f"Total skills: {len(mapping)}")

for status, count in status_counts.items():
    print(f"{status}: {count}")

print(f"Saved: {OUTPUT_FILE}")