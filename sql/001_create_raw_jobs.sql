CREATE TABLE IF NOT EXISTS raw_jobs (
    id          BIGSERIAL PRIMARY KEY,
    source      TEXT        NOT NULL,
    external_id TEXT        NOT NULL,
    fetched_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    payload     JSONB       NOT NULL,
    UNIQUE (source, external_id)
);
