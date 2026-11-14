import csv
import os
import sys

import psycopg2
from dotenv import load_dotenv

from src.processing.skills import SKILLS

load_dotenv()

OUT_PATH = "data/labels.csv"
SAMPLE_SIZE = 30


def main() -> None:
    if os.path.exists(OUT_PATH):
        print(f"{OUT_PATH} already exists - not overwriting your labels.")
        print("Delete or rename it first if you really want a fresh export.")
        sys.exit(1)

    os.makedirs("data", exist_ok=True)
    conn = psycopg2.connect(os.environ["DATABASE_URL"])
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, title, description FROM jobs ORDER BY id LIMIT %s",
                (SAMPLE_SIZE,),
            )
            rows = cur.fetchall()
    finally:
        conn.close()

    with open(OUT_PATH, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["job_id", "title", "description", "true_skills", "done"])
        for job_id, title, description in rows:
            writer.writerow([job_id, title or "", description or "", "", ""])

    print(f"Wrote {len(rows)} jobs to {OUT_PATH}")
    print("Fill 'true_skills' (separated by semicolons) and put y in 'done'.")
    print("Allowed skill names:")
    print("; ".join(sorted(SKILLS)))


if __name__ == "__main__":
    main()
