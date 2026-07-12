-- gen_random_uuid() Postgres 13+ mein core mein available hai
CREATE TABLE IF NOT EXISTS jobs (
  id          UUID PRIMARY KEY,
  document_id UUID NOT NULL,
  filename    TEXT,
  status      TEXT NOT NULL DEFAULT 'processing',  -- processing | done | failed
  error       TEXT,
  created_at  TIMESTAMPTZ DEFAULT now(),
  updated_at  TIMESTAMPTZ DEFAULT now()
);
