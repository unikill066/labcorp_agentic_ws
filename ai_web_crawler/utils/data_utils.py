import csv
from models.job import Job


def is_duplicate_venue(job_id: str, seen_ids: set) -> bool:
    return job_id in seen_ids


def is_complete_venue(job: dict, required_keys: list) -> bool:
    return all(key in job for key in required_keys)


def save_jobs_to_csv(jobs: list, filename: str):
    if not jobs:
        print("No jobs to save.")
        return

    fieldnames = Job.model_fields.keys()

    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(jobs)
    print(f"Saved {len(jobs)} jobs to '{filename}'.")