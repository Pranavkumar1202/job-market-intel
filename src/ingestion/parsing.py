def get_external_id(job: dict) -> str:
    return str(job["id"])


def extract_fields(job: dict) -> dict:
    """Pull the fields we care about from one raw Adzuna job."""
    return {
        "external_id": get_external_id(job),
        "title": job.get("title"),
        "company": (job.get("company") or {}).get("display_name"),
        "location": (job.get("location") or {}).get("display_name"),
        "salary_min": job.get("salary_min"),
        "salary_max": job.get("salary_max"),
        "description": job.get("description"),
        "url": job.get("redirect_url"),
        "created": job.get("created"),
    }