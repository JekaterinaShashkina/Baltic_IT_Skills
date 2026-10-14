import json
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).resolve().parent.parent
FILE = BASE_DIR / "data" / "processed" / "meetfrank_baltic_jobs.json"

with open(FILE, encoding="utf-8") as f:
    data = json.load(f)

# Если файл содержит объект с ключом jobs
jobs = data["jobs"] if isinstance(data, dict) else data

grouped = defaultdict(list)

for job in jobs:
    grouped[str(job["id"])].append(job)

multicountry = {
    job_id: records
    for job_id, records in grouped.items()
    if len(set(job["country"] for job in records)) > 1
}

print(f"Всего записей: {len(jobs)}")
print(f"Вакансий в нескольких странах: {len(multicountry)}")

fields = [
    "title",
    "company",
    "location",
    "remote_type",
    "speciality",
    "seniorities",
    "employment_type",
    "published_at",
    "apply_url",
]

differences = defaultdict(list)

for job_id, records in multicountry.items():
    countries = sorted(set(job["country"] for job in records))

    print(f"\nJob ID: {job_id} | Countries: {', '.join(countries)}")

    skill_sets = [
        set(job.get("skills") or [])
        for job in records
    ]

    if all(skills == skill_sets[0] for skills in skill_sets):
        print("  Skills: IDENTICAL")
    else:
        print("  Skills: DIFFERENT")
        differences["skills"].append(job_id)

        for job in records:
            print(f"    {job['country']}: {job.get('skills')}")

    for field in fields:
        values = [
            json.dumps(job.get(field), sort_keys=True, ensure_ascii=False)
            for job in records
        ]

        if len(set(values)) > 1:
            differences[field].append(job_id)
            print(f"  Different field: {field}")

print("\n=== SUMMARY ===")

if not differences:
    print("Все проверенные поля совпадают.")
else:
    for field, ids in sorted(differences.items()):
        print(f"{field}: {len(ids)} вакансий с различиями")