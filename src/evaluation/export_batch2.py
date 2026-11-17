"""Export a FRESH batch of 30 jobs for an unbiased second evaluation.

It moves your first label file to data/labels_batch1.csv, then writes a new
data/labels.csv containing 30 jobs that were not in the first batch.
The labelling and evaluation scripts keep working unchanged.
"""
import csv
import os
import sys

import psycopg2
from dotenv import load_dotenv

load_dotenv()

LABELS = "data/labels.csv"
BATCH1 = "data/labels_batch1.csv"
SAMPLE_SIZE = 30


def main() -> None:
    if os.path.exists(BATCH1):
        print(f"{BATCH1} already exists - batch 2 was already created.")
        print("Delete or rename it first if you really want to start again.")
        sys.exit(1)
    if not os.path.exists(LABELS):
        print(f"{LABELS} not found.")
        sys.exit(1)

    with open(LABELS, newline="", encoding="utf-8-sig") as f:
        used_ids = [int(r["job_id"]) for r in csv.DictReader(f)]

    conn = psycopg2.connect(os.environ["DATABASE_URL"])
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, title, description
                FROM jobs
                WHERE NOT (id = ANY(%s)) AND description IS NOT NULL
                ORDER BY id DESC
                LIMIT %s
                """,
                (used_ids, SAMPLE_SIZE),
            )
            rows = cur.fetchall()
    finally:
        conn.close()

    os.replace(LABELS, BATCH1)
    with open(LABELS, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["job_id", "title", "description", "true_skills", "done"])
        for job_id, title, description in rows:
            writer.writerow([job_id, title or "", description or "", "", ""])

    print(f"Old labels kept in {BATCH1}")
    print(f"Wrote {len(rows)} fresh jobs to {LABELS}")
    print("Now run: python -m src.evaluation.label_jobs")


if __name__ == "__main__":
    main()
