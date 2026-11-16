import io
import os
from contextlib import asynccontextmanager

import psycopg2
from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, Query, UploadFile

from src.matching.embed_jobs import MODEL_NAME
from src.matching.match_resume import load_jobs
from src.matching.scoring import rank_jobs, skill_gaps
from src.processing.skills import extract_skills

load_dotenv()

MAX_UPLOAD_BYTES = 5 * 1024 * 1024
state = {}


def connect():
    return psycopg2.connect(os.environ["DATABASE_URL"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the model and the job embeddings once, not on every request.
    from sentence_transformers import SentenceTransformer

    state["model"] = SentenceTransformer(MODEL_NAME)
    conn = connect()
    try:
        state["jobs"] = load_jobs(conn)
    finally:
        conn.close()
    yield
    state.clear()


app = FastAPI(title="Job Market Intelligence API", lifespan=lifespan)


def text_from_upload(filename: str, data: bytes) -> str:
    if (filename or "").lower().endswith(".pdf"):
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(data))
        return "\n".join((page.extract_text() or "") for page in reader.pages)
    return data.decode("utf-8", errors="ignore")


@app.get("/health")
def health():
    return {"status": "ok", "jobs_loaded": len(state.get("jobs", []))}


@app.get("/jobs")
def list_jobs(
    q: str | None = Query(None, description="text to look for in the job title"),
    limit: int = Query(20, ge=1, le=100),
):
    pattern = f"%{q}%" if q else None
    conn = connect()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, title, company, city, category, url
                FROM jobs
                WHERE (%s IS NULL OR title ILIKE %s)
                ORDER BY id DESC
                LIMIT %s
                """,
                (pattern, pattern, limit),
            )
            rows = cur.fetchall()
    finally:
        conn.close()
    return [
        {"id": r[0], "title": r[1], "company": r[2], "city": r[3],
         "category": r[4], "url": r[5]}
        for r in rows
    ]


@app.get("/trends/skills")
def skill_trends(limit: int = Query(15, ge=1, le=50)):
    conn = connect()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT s.name, COUNT(*) AS jobs
                FROM job_skills js
                JOIN skills s ON s.id = js.skill_id
                GROUP BY s.name
                ORDER BY jobs DESC, s.name
                LIMIT %s
                """,
                (limit,),
            )
            rows = cur.fetchall()
    finally:
        conn.close()
    return [{"skill": name, "jobs": count} for name, count in rows]


@app.post("/match")
def match(
    file: UploadFile = File(..., description="resume as .pdf or .txt"),
    top: int = Query(10, ge=1, le=50),
):
    data = file.file.read(MAX_UPLOAD_BYTES + 1)
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File is larger than 5 MB.")

    try:
        text = text_from_upload(file.filename, data)
    except Exception:
        raise HTTPException(status_code=422, detail="Could not read that file.")
    if not text.strip():
        raise HTTPException(
            status_code=422,
            detail="No text found in the file (a scanned PDF has no text layer).",
        )

    jobs = state.get("jobs")
    if not jobs:
        raise HTTPException(status_code=503, detail="No jobs are loaded yet.")

    resume_skills = extract_skills(text)
    resume_vec = state["model"].encode(text, normalize_embeddings=True)
    matches = rank_jobs(resume_vec, resume_skills, jobs, top_n=top)
    gaps = skill_gaps(rank_jobs(resume_vec, resume_skills, jobs, top_n=30))[:8]

    return {
        "resume_skills": sorted(resume_skills),
        "matches": matches,
        "skill_gaps": [{"skill": s, "jobs": n} for s, n in gaps],
    }
