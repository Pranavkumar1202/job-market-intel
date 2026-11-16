CREATE TABLE IF NOT EXISTS job_embeddings (
    job_id     BIGINT PRIMARY KEY REFERENCES jobs(id) ON DELETE CASCADE,
    model      TEXT   NOT NULL,
    embedding  REAL[] NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
