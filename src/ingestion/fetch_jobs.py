import logging
import os
import time

import psycopg2
import requests
from dotenv import load_dotenv
from psycopg2.extras import Json

from src.ingestion.parsing import get_external_id

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

BASE_URL = "https://api.adzuna.com/v1/api/jobs/{country}/search/{page}"
SEARCH_TERMS = ["data analyst"]
SOURCE = "adzuna"


def fetch_page(term: str, page: int, country: str = "in") -> list[dict]:
    params = {
        "app_id": os.environ["ADZUNA_APP_ID"],
        "app_key": os.environ["ADZUNA_APP_KEY"],
        "results_per_page": 50,
        "what": term,
        "content-type": "application/json",
    }
    resp = requests.get(
        BASE_URL.format(country=country, page=page), params=params, timeout=30
    )
    resp.raise_for_status()
    return resp.json().get("results", [])


def save_jobs(conn, jobs: list[dict]) -> int:
    inserted = 0
    with conn.cursor() as cur:
        for job in jobs:
            cur.execute(
                """
                INSERT INTO raw_jobs (source, external_id, payload)
                VALUES (%s, %s, %s)
                ON CONFLICT (source, external_id) DO NOTHING
                """,
                (SOURCE, get_external_id(job), Json(job)),
            )
            inserted += cur.rowcount
    conn.commit()
    return inserted


def main(pages_per_term: int = 1) -> None:
    conn = psycopg2.connect(os.environ["DATABASE_URL"])
    total_fetched = total_inserted = 0
    try:
        for term in SEARCH_TERMS:
            for page in range(1, pages_per_term + 1):
                try:
                    jobs = fetch_page(term, page)
                except requests.RequestException as exc:
                    log.error("Fetch failed for %r page %d: %s", term, page, exc)
                    continue
                if not jobs:
                    break
                inserted = save_jobs(conn, jobs)
                total_fetched += len(jobs)
                total_inserted += inserted
                log.info("%r page %d: fetched %d, new %d", term, page, len(jobs), inserted)
                time.sleep(1)
    finally:
        conn.close()
    log.info("Done. Fetched %d, inserted %d new.", total_fetched, total_inserted)


if __name__ == "__main__":
    main()