from ..database import create_tables, finish_pipeline_run, save_country_run, save_pipeline_stats, start_pipeline_run
from ..meetfrank.fetch_meetfrank import fetch_all_jobs, fetch_jobs, normalize_job
from ..meetfrank.update_meetfrank import update_meetfrank
from ..config import COUNTRIES
from ..esco.match_esco import check_esco_matches

def run_pipeline():
    create_tables()
    run_id = start_pipeline_run()

    try:
        all_jobs = []
        for country in COUNTRIES:
            try:
                jobs = fetch_jobs(country)


                if not jobs:
                    raise ValueError(f"No jobs returned for {country}")
                
                normalized_jobs = [
                    normalize_job(job, country)
                    for job in jobs
                ]
                all_jobs.extend(normalized_jobs)
                save_country_run(
                    run_id, country, "success", len(jobs)
                )
                print(f"{country}: {len(jobs)} jobs received")
            except Exception as error:
                save_country_run(
                    run_id, country, "failed", error_message=str(error)
                )
                raise

        stats = update_meetfrank(all_jobs, run_id=run_id)
        save_pipeline_stats(run_id, stats)

    except Exception as error:
        finish_pipeline_run(run_id, "failed", str(error))
        raise
    else:
        finish_pipeline_run(run_id,  "success")
        print(f"ETL pipeline completed successfully! Run ID: {run_id}")

    # Run ESCO matching after the MeetFrank pipeline completes
    try:
        esco_stats = check_esco_matches(limit=20)
        print(f"ESCO matching statistics: {esco_stats}")
    except Exception as error:
        print(f"ESCO matching stage failed: {error}")


if __name__ == "__main__":
    run_pipeline()