CREATE TABLE IF NOT EXISTS skills (
    id       SERIAL PRIMARY KEY,
    name     TEXT NOT NULL UNIQUE,
    category TEXT
);

CREATE TABLE IF NOT EXISTS job_skills (
    job_id   BIGINT  NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    skill_id INTEGER NOT NULL REFERENCES skills(id),
    PRIMARY KEY (job_id, skill_id)
);