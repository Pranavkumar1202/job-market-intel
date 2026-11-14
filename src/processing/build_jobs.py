import logging
import os

import psycopg2
from dotenv import load_dotenv

from src.processing.clean import clean_job

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

INSERT_SQL = """
INSERT INTO jobs (raw_id, source, external_id, title, title_normalized, company,
                  location, city, category, contract_type, contract_time,
                  salary_min, salary_max, description, url, posted_at, dedup_key)
VALUES (%(raw_id)s, %(source)s, %(external_id)s, %(title)s, %(title_normalized)s,
        %(company)s, %(location)s, %(city)s, %(category)s, %(contract_type)s,
        %(contract_time)s, %(salary_min)s, %(salary_max)s, %(description)s,
        %(url)s, %(posted_at)s, %(dedup_key)s)
ON CONFLICT (dedup_key) DO NOTHING
"""


def main() -> None:
    conn = psycopg2.connect(os.environ["DATABASE_URL"])
    read = inserted = failed = 0
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT r.id, r.source, r.payload FROM raw_jobs r
                WHERE NOT EXISTS (SELECT 1 FROM jobs j
                                  WHERE j.source = r.source
                                    AND j.external_id = r.external_id)
            """)
            rows = cur.fetchall()
            for raw_id, source, payload in rows:
                read += 1
                try:
                    record = clean_job(payload)
                    record.update({"raw_id": raw_id, "source": source})
                    cur.execute(INSERT_SQL, record)
                    inserted += cur.rowcount
                except Exception as exc:
                    failed += 1
                    log.error("Row %s failed: %s", raw_id, exc)
        conn.commit()
    finally:
        conn.close()
    log.info("Read %d raw rows, inserted %d, skipped duplicates %d, failed %d",
             read, inserted, read - inserted - failed, failed)


if __name__ == "__main__":
    main()