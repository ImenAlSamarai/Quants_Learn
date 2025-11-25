-- Phase 2: Add professional profile columns to users table
-- Run with: psql -d quant_learn -f add_phase2_columns.sql

\echo '📝 Adding Phase 2 columns to users table...'

ALTER TABLE users ADD COLUMN IF NOT EXISTS email VARCHAR(200);
ALTER TABLE users ADD COLUMN IF NOT EXISTS phone VARCHAR(50);
ALTER TABLE users ADD COLUMN IF NOT EXISTS cv_url VARCHAR(500);
ALTER TABLE users ADD COLUMN IF NOT EXISTS linkedin_url VARCHAR(500);
ALTER TABLE users ADD COLUMN IF NOT EXISTS education_level VARCHAR(50);
ALTER TABLE users ADD COLUMN IF NOT EXISTS "current_role" VARCHAR(200);  -- Quoted: PostgreSQL reserved keyword
ALTER TABLE users ADD COLUMN IF NOT EXISTS years_experience INTEGER;
ALTER TABLE users ADD COLUMN IF NOT EXISTS target_roles JSON;

\echo '✅ Phase 2 columns added successfully!'
