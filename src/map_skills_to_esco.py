import json
from pathlib import Path
import requests
import time
from collections import Counter

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "data" / "processed" / "meetfrank_baltic_jobs.json"
OUTPUT_FILE = BASE_DIR / "data" / "processed" / "esco_skill_mapping_candidates.json"

ESCO_URL = "https://ec.europa.eu/esco/api/search"


# 1. Загружаем вакансии MeetFrank
with open(INPUT_FILE, "r", encoding="utf-8") as file:
    jobs = json.load(file)


# 2. Собираем уникальные skills и одновременно считаем частоту
skill_counter = Counter()

for job in jobs:
    unique_skills = set(job.get("skills", []))

    for skill in unique_skills:
        skill_counter[skill] += 1


print(f"Unique MeetFrank skills: {len(skill_counter)}")


# 3. Для каждого skill ищем кандидатов в ESCO
mapping_results = {}

for number, (skill, frequency) in enumerate(
    skill_counter.most_common(),
    start=1
):
    print(
        f"[{number}/{len(skill_counter)}] "
        f"Searching ESCO: {skill}"
    )

    params = {
        "text": skill,
        "language": "en",
        "type": "skill",
        "limit": 5,
        "selectedVersion": "v1.2.0"
    }

    try:
        response = requests.get(
            ESCO_URL,
            params=params,
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        results = data.get("_embedded", {}).get("results", [])

        candidates = []

        for result in results:
            candidates.append({
                "title": result.get("title"),
                "uri": result.get("uri"),
                "search_hit": result.get("searchHit")
            })

        mapping_results[skill] = {
            "meetfrank_frequency": frequency,
            "esco_total_results": data.get("total", 0),
            "candidates": candidates
        }

    except requests.RequestException as error:
        print(f"ERROR: {skill}: {error}")

        mapping_results[skill] = {
            "meetfrank_frequency": frequency,
            "esco_total_results": None,
            "candidates": [],
            "error": str(error)
        }

    # Немного бережём API
    time.sleep(0.2)


# 4. Сохраняем результаты
with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
    json.dump(
        mapping_results,
        file,
        ensure_ascii=False,
        indent=4
    )


print("\nFinished.")
print(f"Skills processed: {len(mapping_results)}")
print(f"Saved: {OUTPUT_FILE}")