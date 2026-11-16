import requests

from ..logger import get_logger
from ..config import (
    COUNTRIES,
    MEETFRANK_API_URL,
    MEETFRANK_SPECIALITY,
    MEETFRANK_PAGE_SIZE,
    REQUEST_TIMEOUT,
)

logger = get_logger(__name__)


def fetch_jobs(country):
    all_jobs = []
    page = 1
    seen_ids = set()

    logger.info("Fetching MeetFrank jobs for %s", country)
    # Fetch all available pages of job postings
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

        logger.debug(
            "%s: page %s received, %s jobs",
            country,
            page,
            len(data["jobs"]),
        )

        # Validate the number of retrieved jobs
        if page == 1:
            expected_total = data["total"]

        if data["page"] != page:
            raise ValueError(
                f"{country}: expected page {page}, got {data['page']}"
            )
        # Detect duplicate job IDs within the same country
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

    # Verify that all expected jobs were retrieved
    if len(all_jobs) != expected_total:
        raise ValueError(
            f"{country}: incomplete download. "
            f"Expected {expected_total}, received {len(all_jobs)}"
        )
    logger.info(
        "%s: download completed. Jobs %s, pages fetched: %s",
        country,
        len(all_jobs),
        page,
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

    for country in COUNTRIES:
        jobs = fetch_jobs(country)

        for job in jobs:
            normalized = normalize_job(job, country)
            all_jobs.append(normalized)

    return all_jobs


if __name__ == "__main__":
    from ..logger import setup_logging

    setup_logging()
    jobs = fetch_all_jobs()

    logger.info("Total country records: %s", len(jobs))
    logger.info(
        "Unique job IDs: %s",
        len({job["id"] for job in jobs}),
    )
