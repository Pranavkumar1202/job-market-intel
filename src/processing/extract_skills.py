import logging
import os

import psycopg2
from dotenv import load_dotenv

from src.processing.skills import extract_skills, skill_catalog

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)


def main() -> None:
    conn = psycopg2.connect(os.environ["DATABASE_URL"])
    links = jobs_with_skills = 0
    try:
        with conn.cursor() as cur:
            for name, category in skill_catalog():
                cur.execute(
                    "INSERT INTO skills (name, category) VALUES (%s, %s) "
                    "ON CONFLICT (name) DO NOTHING",
                    (name, category),
                )
            cur.execute("SELECT name, id FROM skills")
            ids = dict(cur.fetchall())

            cur.execute("SELECT id, title, description FROM jobs")
            rows = cur.fetchall()
            for job_id, title, description in rows:
                found = extract_skills(title, description)
                if found:
                    jobs_with_skills += 1
                for skill in found:
                    cur.execute(
                        "INSERT INTO job_skills (job_id, skill_id) VALUES (%s, %s) "
                        "ON CONFLICT DO NOTHING",
                        (job_id, ids[skill]),
                    )
                    links += cur.rowcount
        conn.commit()
    finally:
        conn.close()
    log.info("Jobs: %d, with at least one skill: %d, new links: %d",
             len(rows), jobs_with_skills, links)


if __name__ == "__main__":
    main()
