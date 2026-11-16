import numpy as np

SIM_WEIGHT = 0.7
SKILL_WEIGHT = 0.3
# A job that lists fewer than this many skills gets a proportionally smaller
# skill bonus, because "1 of 1 skills matched" says very little.
FULL_CONFIDENCE_SKILLS = 3


def rank_jobs(resume_vec, resume_skills, jobs, top_n=10):
    """Rank jobs for a resume.

    resume_vec:    normalised embedding of the resume (list or array)
    resume_skills: set of skill names found in the resume
    jobs:          list of dicts with at least 'embedding' (normalised) and
                   'skills' (iterable of skill names); other keys are passed through

    score = 0.7 * cosine similarity + 0.3 * overlap * confidence
    overlap    = share of the job's skills the resume has
    confidence = min(number of skills detected in the job, 3) / 3
    A job with no detected skills gets 0 for the skill part, and is flagged
    with skill_overlap = None so the caller can show that.
    """
    if not jobs:
        return []

    resume_skills = set(resume_skills)
    matrix = np.array([j["embedding"] for j in jobs], dtype=float)
    sims = matrix @ np.asarray(resume_vec, dtype=float)

    results = []
    for job, sim in zip(jobs, sims):
        job_skills = set(job["skills"])
        matched = job_skills & resume_skills
        missing = job_skills - resume_skills
        overlap = len(matched) / len(job_skills) if job_skills else None
        confidence = min(len(job_skills), FULL_CONFIDENCE_SKILLS) / FULL_CONFIDENCE_SKILLS
        score = SIM_WEIGHT * float(sim) + SKILL_WEIGHT * (overlap or 0.0) * confidence

        item = {k: v for k, v in job.items() if k not in ("embedding", "skills")}
        item.update(
            similarity=float(sim),
            skill_overlap=overlap,
            score=score,
            matched=sorted(matched),
            missing=sorted(missing),
        )
        results.append(item)

    results.sort(key=lambda r: r["score"], reverse=True)
    return results[:top_n]


def skill_gaps(results):
    """Count how often each skill is missing across the ranked jobs."""
    counts = {}
    for r in results:
        for skill in r["missing"]:
            counts[skill] = counts.get(skill, 0) + 1
    return sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
