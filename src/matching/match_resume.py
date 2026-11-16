import argparse
import os
import sys

import psycopg2
from dotenv import load_dotenv

from src.matching.embed_jobs import MODEL_NAME
from src.matching.scoring import rank_jobs, skill_gaps
from src.processing.skills import extract_skills

load_dotenv()


def read_resume(path):
    if path.lower().endswith(".pdf"):
        from pypdf import PdfReader

        reader = PdfReader(path)
        return "\n".join((page.extract_text() or "") for page in reader.pages)
    with open(path, encoding="utf-8") as f:
        return f.read()


def load_jobs(conn):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT j.id, j.title, j.company, j.city, j.url, e.embedding
            FROM jobs j
            JOIN job_embeddings e ON e.job_id = j.id
            """
        )
        job_rows = cur.fetchall()
        cur.execute(
            """
            SELECT js.job_id, s.name
            FROM job_skills js
            JOIN skills s ON s.id = js.skill_id
            """
        )
        skills = {}
        for job_id, name in cur.fetchall():
            skills.setdefault(job_id, set()).add(name)

    return [
        {
            "id": job_id,
            "title": title,
            "company": company,
            "city": city,
            "url": url,
            "embedding": embedding,
            "skills": skills.get(job_id, set()),
        }
        for job_id, title, company, city, url, embedding in job_rows
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Rank stored jobs for a resume.")
    parser.add_argument("resume", help="path to a .pdf or .txt resume")
    parser.add_argument("--top", type=int, default=10, help="how many jobs to show")
    args = parser.parse_args()

    if not os.path.exists(args.resume):
        print(f"Resume file not found: {args.resume}")
        sys.exit(1)

    text = read_resume(args.resume)
    if not text.strip():
        print("No text could be read from the resume (scanned PDF?).")
        sys.exit(1)

    resume_skills = extract_skills(text)
    print(f"Resume skills found ({len(resume_skills)}): {', '.join(sorted(resume_skills)) or 'none'}")

    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(MODEL_NAME)
    resume_vec = model.encode(text, normalize_embeddings=True)

    conn = psycopg2.connect(os.environ["DATABASE_URL"])
    try:
        jobs = load_jobs(conn)
    finally:
        conn.close()

    if not jobs:
        print("No jobs with embeddings found. Run the embedding step first.")
        sys.exit(1)

    results = rank_jobs(resume_vec, resume_skills, jobs, top_n=args.top)

    print(f"\nTop {len(results)} of {len(jobs)} jobs:\n")
    for i, r in enumerate(results, start=1):
        place = f" ({r['city']})" if r["city"] else ""
        overlap = (
            f"{r['skill_overlap']:.0%}" if r["skill_overlap"] is not None
            else "no skills detected in ad"
        )
        print(f"{i}. {r['title']} - {r['company'] or 'unknown company'}{place}")
        print(f"   score {r['score']:.2f} | similarity {r['similarity']:.2f} | skill overlap {overlap}")
        print(f"   You have:   {', '.join(r['matched']) or '-'}")
        print(f"   You lack:   {', '.join(r['missing']) or '-'}")
        if r["url"]:
            print(f"   {r['url']}")
        print()

    wider = rank_jobs(resume_vec, resume_skills, jobs, top_n=30)
    gaps = skill_gaps(wider)[:8]
    if gaps:
        print("Skills most often missing across your top 30 matches:")
        for skill, count in gaps:
            print(f"  {skill}: {count} jobs")
    else:
        print("No skill gaps found across your top 30 matches.")


if __name__ == "__main__":
    main()
