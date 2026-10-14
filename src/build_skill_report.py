import json
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "processed"

with open(DATA_DIR / "meetfrank_baltic_jobs.json", encoding="utf-8") as file:
    jobs = json.load(file)

with open(DATA_DIR / "esco_skill_mapping.json", encoding="utf-8") as file:
    mapping = json.load(file)

with open(DATA_DIR / "esco_skill_occupations.json", encoding="utf-8") as file:
    occupations = json.load(file)

# Считаем количество вакансий с каждым навыком по странам
statistics = defaultdict(lambda: defaultdict(int))
country_totals = defaultdict(int)

for job in jobs:
    country = job["country"]
    country_totals[country] += 1

    for skill in set(job.get("skills", [])):
        statistics[country][skill] += 1

# Для первого отчёта возьмём понятные технологии
selected_skills = [
    "Python",
    "Java",
    "JavaScript",
    "React",
    "Docker",
    "Kubernetes"
]

for skill in selected_skills:
    info = mapping.get(skill)

    if not info or info["status"] not in ("exact", "broader"):
        print(f"\n{skill}: no confirmed ESCO mapping")
        continue

    uri = info["esco_uri"]
    esco_info = occupations.get(uri, {})

    print(f"\n{'=' * 55}")
    print(f"MeetFrank skill: {skill}")
    print(f"ESCO skill: {info['esco_title']}")
    print(f"Mapping type: {info['status']}")

    print("\nDemand by country:")

    for country in ["estonia", "latvia", "lithuania"]:
        count = statistics[country][skill]
        total = country_totals[country]
        percentage = count / total * 100 if total else 0

        print(f"  {country}: {count}/{total} ({percentage:.1f}%)")

    essential = esco_info.get("essential_occupations", [])
    optional = esco_info.get("optional_occupations", [])

    print(f"\nESCO occupations: {len(essential)} essential, "
        f"{len(optional)} optional")

    print("Essential occupations:")
    for occupation in essential[:5]:
        print(f"  - {occupation['title']}")