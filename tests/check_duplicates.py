import json
from collections import defaultdict

INPUT_FILE = "meetfrank_baltic_jobs.json"

with open(INPUT_FILE, "r", encoding="utf-8") as file:
    jobs = json.load(file)

# Для каждого ID сохраняем страны, в которых встретилась вакансия
jobs_by_id = defaultdict(list)

for job in jobs:
    jobs_by_id[job["id"]].append(job)

# Оставляем только ID, которые встретились больше одного раза
duplicates = {
    job_id: items
    for job_id, items in jobs_by_id.items()
    if len(items) > 1
}

print(f"Total records: {len(jobs)}")
print(f"Unique vacancy IDs: {len(jobs_by_id)}")
print(f"Duplicated vacancy IDs: {len(duplicates)}")

print("\nDuplicated vacancies:")

for job_id, items in duplicates.items():
    title = items[0]["title"]
    company = items[0]["company"]
    countries = [item["country"] for item in items]

    print(f"\n{job_id}")
    print(f"{title} | {company}")
    print(f"Countries: {', '.join(countries)}")
