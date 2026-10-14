import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

countries = ["estonia", "latvia", "lithuania"]

all_jobs = []

for country in countries:
    filename = BASE_DIR / "data" / "raw" / f"meetfrank_{country}_jobs.json"

    with open(filename, "r", encoding="utf-8") as file:
        data = json.load(file)

    jobs = data.get("jobs", [])

    for job in jobs:
        normalized_job = {
            "id": job.get("id"),
            "country": country,
            "title": job.get("title"),
            "company": job.get("company"),
            "location": job.get("location"),
            "remote_type": job.get("remote", {}).get("type"),
            "speciality": job.get("speciality"),
            "seniorities": job.get("seniorities", []),
            "employment_type": job.get("employmentType"),
            "skills": job.get("skills", []),
            "published_at": job.get("publishedAt"),
            "apply_url": job.get("applyUrl")
        }

        all_jobs.append(normalized_job)

output_file = BASE_DIR / "data" / "processed" / "meetfrank_baltic_jobs.json"

with open(output_file, "w", encoding="utf-8") as file:
    json.dump(all_jobs, file, ensure_ascii=False, indent=4)

print(f"Total jobs: {len(all_jobs)}")
print(f"Saved: {output_file}")