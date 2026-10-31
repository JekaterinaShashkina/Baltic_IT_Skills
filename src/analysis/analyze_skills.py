import json
from collections import Counter
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "data" / "processed" / "meetfrank_baltic_jobs.json"
OUTPUT_FILE = BASE_DIR / "data" / "processed" / "skill_statistics.json"

with open(INPUT_FILE, "r", encoding="utf-8") as file:
    jobs = json.load(file)

countries = ["estonia", "latvia", "lithuania"]

statistics = {}

for country in countries:

    # Все вакансии, относящиеся к этой стране
    country_jobs = [
        job for job in jobs
        if job["country"] == country
    ]

    total_jobs = len(country_jobs)

    skill_counter = Counter()

    for job in country_jobs:
        # set нужен, чтобы один skill не посчитался
        # дважды внутри одной вакансии
        unique_skills = set(job.get("skills", []))

        for skill in unique_skills:
            skill_counter[skill] += 1

    country_statistics = []

    for skill, count in skill_counter.most_common():

        percentage = round(
            count / total_jobs * 100,
            1
        )

        country_statistics.append({
            "skill": skill,
            "vacancy_count": count,
            "percentage": percentage
        })

    statistics[country] = {
        "total_jobs": total_jobs,
        "skills": country_statistics
    }


with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
    json.dump(
        statistics,
        file,
        ensure_ascii=False,
        indent=4
    )


# Показываем TOP 15 в консоли
for country in countries:

    print(f"\n{'=' * 40}")
    print(country.upper())
    print(f"Vacancies: {statistics[country]['total_jobs']}")
    print(f"{'=' * 40}")

    for item in statistics[country]["skills"][:15]:
        print(
            f"{item['skill']:<30}"
            f"{item['vacancy_count']:>3} "
            f"({item['percentage']:>5.1f}%)"
        )


print(f"\nSaved: {OUTPUT_FILE}")