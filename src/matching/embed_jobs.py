import logging
import os

import psycopg2
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
BATCH_SIZE = 32


def job_text(title, description):
    return f"{title or ''}. {description or ''}".strip()


def main() -> None:
    conn = psycopg2.connect(os.environ["DATABASE_URL"])
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT j.id, j.title, j.description
                FROM jobs j
                WHERE NOT EXISTS (
                    SELECT 1 FROM job_embeddings e WHERE e.job_id = j.id
                )
                ORDER BY j.id
                """
            )
            rows = cur.fetchall()
            if not rows:
                log.info("Every job already has an embedding. Nothing to do.")
                return

            log.info("Loading model %s (first run downloads about 90 MB)...", MODEL_NAME)
            model = SentenceTransformer(MODEL_NAME)
            texts = [job_text(title, desc) for _, title, desc in rows]
            log.info("Embedding %d jobs...", len(texts))
            vectors = model.encode(
                texts,
                batch_size=BATCH_SIZE,
                normalize_embeddings=True,
                show_progress_bar=True,
            )

            for (job_id, _, _), vec in zip(rows, vectors):
                cur.execute(
                    "INSERT INTO job_embeddings (job_id, model, embedding) "
                    "VALUES (%s, %s, %s) ON CONFLICT (job_id) DO NOTHING",
                    (job_id, MODEL_NAME, vec.tolist()),
                )
        conn.commit()
        log.info("Stored %d embeddings.", len(rows))
    finally:
        conn.close()


if __name__ == "__main__":
    main()
