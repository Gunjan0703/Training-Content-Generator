-- Database bootstrap for corporate-training-ai
-- Safe to run multiple times (IF NOT EXISTS used where applicable)

-- Optional: create separate schema to isolate app tables
CREATE SCHEMA IF NOT EXISTS training AUTHORIZATION CURRENT_USER;

-- Switch to schema for subsequent objects
SET search_path TO training, public;

-- Ensure required extensions are available (comment out if not needed/allowed)
-- uuid-ossp: for UUID generation
-- pgcrypto: for cryptographic functions (e.g., digest, gen_random_uuid in newer versions)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Media storage table (BYTEA for binary objects like images)
CREATE TABLE IF NOT EXISTS training.media_objects (
  id SERIAL PRIMARY KEY,
  filename TEXT NOT NULL,
  mimetype TEXT NOT NULL,
  size_bytes BIGINT NOT NULL,
  data BYTEA NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Index to speed up recent media queries
CREATE INDEX IF NOT EXISTS idx_media_objects_created_at ON training.media_objects (created_at DESC);

-- Transcripts table (optional; used by multimedia service if storing transcripts)
CREATE TABLE IF NOT EXISTS training.transcripts (
  id SERIAL PRIMARY KEY,
  source_uri TEXT NOT NULL,
  text TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_transcripts_created_at ON training.transcripts (created_at DESC);

-- Optional app role with least-privilege access
DO $$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'app_user') THEN
    CREATE ROLE app_user LOGIN PASSWORD 'changeme-app';
  END IF;
END
$$;

-- Grant minimal privileges to app_user on training schema objects
GRANT USAGE ON SCHEMA training TO app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON training.media_objects TO app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON training.transcripts TO app_user;

-- (Optional) future tables: user_profiles, jobs, audit_logs, etc.
-- Example template:
-- CREATE TABLE IF NOT EXISTS training.audit_logs (
--   id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
--   actor TEXT NOT NULL,
--   action TEXT NOT NULL,
--   details JSONB,
--   created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
-- );
-- GRANT INSERT, SELECT ON training.audit_logs TO app_user;
