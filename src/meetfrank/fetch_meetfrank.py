import requests

from ..config import (
    MEETFRANK_API_URL,
    MEETFRANK_SPECIALITY,
    MEETFRANK_PAGE_SIZE,
    REQUEST_TIMEOUT,
)

def fetch_jobs(country):
    all_jobs = []
    page = 1
    seen_ids = set()

    # Цикл получения страниц
    while True:
        params = {
            "country": country,
            "speciality": MEETFRANK_SPECIALITY,
            "pageSize": MEETFRANK_PAGE_SIZE,
            "page": page
        }
        response = requests.get(MEETFRANK_API_URL, params=params, timeout=REQUEST_TIMEOUT)

        response.raise_for_status()

        data = response.json()

        # Проверяем количество полученных вакансий
        if page == 1:
            expected_total = data["total"]

        if data["page"] != page:
            raise ValueError(
                f"{country}: expected page {page}, got {data['page']}"
            )
        # обнаружение повторяющихся вакансий в пределах одной страны
        for job in data["jobs"]:
            job_id = job["id"]

            if job_id in seen_ids:
                raise ValueError(
                    f"{country}: duplicate job ID {job_id}"
                )

            seen_ids.add(job_id)

        all_jobs.extend(data["jobs"])
        if not data.get("hasMore"):
            break
        page += 1

    # Проверяем полноту загрузки после завершения цикла
    if len(all_jobs) != expected_total:
        raise ValueError(
            f"{country}: incomplete download. "
            f"Expected {expected_total}, received {len(all_jobs)}"
        )
    return all_jobs

def normalize_job(raw_job, country):
    remote = raw_job.get("remote") or {}

    return {
        "id": raw_job.get("id"),
        "country": country,
        "title": raw_job.get("title"),
        "company": raw_job.get("company"),
        "location": raw_job.get("location"),
        "remote_type": remote.get("type"),
        "speciality": raw_job.get("speciality"), 
        "seniorities": raw_job.get("seniorities", []), 
        "employment_type": raw_job.get("employmentType"), 
        "skills": raw_job.get("skills", []), 
        "published_at": raw_job.get("publishedAt"), 
        "apply_url": raw_job.get("applyUrl")
    }

def fetch_all_jobs():
    all_jobs = []

    for country in ["estonia", "latvia", "lithuania"]:
        jobs = fetch_jobs(country)

        for job in jobs:
            normalized = normalize_job(job, country)
            all_jobs.append(normalized)

    return all_jobs


if __name__ == "__main__":
    jobs = fetch_all_jobs()

    print("Total country records:", len(jobs))
    print("Unique job IDs:", len(set(job["id"] for job in jobs)))
