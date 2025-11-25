# Phase 2 Migration Guide

## Issue Summary

The Phase 2 migration created new tables (`user_competencies`, `study_sessions`) but did **not** alter the existing `users` table to add the new professional profile columns. This causes the error:

```
psycopg2.errors.UndefinedColumn: column users.email does not exist
```

## Root Cause

SQLAlchemy's `Base.metadata.create_all()` only creates **new** tables - it doesn't modify existing table schemas. The `users` table existed before Phase 2, so the new columns were never added.

## Fix: Add Missing Columns

I've created **two migration options** for you:

### Option 1: Python Script (Recommended)

```bash
cd /home/user/Quants_Learn/backend
python add_phase2_columns.py
```

**Note:** PostgreSQL must be running first!

### Option 2: SQL File (Direct psql)

```bash
cd /home/user/Quants_Learn/backend
psql -d quant_learn -f add_phase2_columns.sql
```

## New Columns Being Added

The migration adds these professional profile columns to the `users` table:

1. `email` VARCHAR(200)
2. `phone` VARCHAR(50)
3. `cv_url` VARCHAR(500)
4. `linkedin_url` VARCHAR(500)
5. `education_level` VARCHAR(50)
6. `"current_role"` VARCHAR(200) ⚠️ **Quoted** (PostgreSQL reserved keyword)
7. `years_experience` INTEGER
8. `target_roles` JSON

## Important Notes

- **Reserved Keyword**: `current_role` is a PostgreSQL reserved keyword and **must** be quoted in SQL
- **Idempotent**: Both migration scripts use `IF NOT EXISTS`, so they're safe to run multiple times
- **No Data Loss**: Only adds columns, doesn't modify existing data

## Steps to Complete Migration

1. **Ensure PostgreSQL is running**:
   ```bash
   # Check if PostgreSQL is running
   ps aux | grep postgres

   # If not, start it (method depends on your setup):
   sudo systemctl start postgresql  # Linux systemd
   # OR
   sudo service postgresql start    # Linux sysvinit
   # OR
   pg_ctl start  # Manual start
   ```

2. **Run the migration**:
   ```bash
   cd /home/user/Quants_Learn/backend
   python add_phase2_columns.py
   ```

3. **Restart the backend**:
   ```bash
   cd /home/user/Quants_Learn/backend
   python -m app.main
   ```

4. **Start the frontend** (in another terminal):
   ```bash
   cd /home/user/Quants_Learn/frontend
   npm run dev
   ```

5. **Test Phase 2 Dashboard**:
   - Navigate to: http://localhost:3000/dashboard
   - Should see professional profile section with completion percentage
   - Should see interview readiness score
   - Should see competencies grid

## Verification

After migrating, verify the columns exist:

```bash
psql -d quant_learn -c "\d users"
```

You should see all 8 new columns listed in the table schema.

## Troubleshooting

### "Connection refused" Error
- PostgreSQL isn't running
- Start PostgreSQL using one of the methods above

### "Database does not exist" Error
- The `quant_learn` database hasn't been created
- Create it: `createdb quant_learn`
- Then run: `python -c "from app.models.database import init_db; init_db()"`

### "syntax error at or near current_role"
- The `current_role` column isn't properly quoted
- Use the scripts I provided - they have the correct quoting

## Files Created

- `add_phase2_columns.py` - Python migration script
- `add_phase2_columns.sql` - SQL migration file
- `PHASE2_MIGRATION_GUIDE.md` - This guide

## What This Fixes

Once migration completes, these Phase 2 features will work:

✅ User dashboard endpoint (`/api/users/{user_id}/dashboard`)
✅ Profile completion percentage calculation
✅ Interview readiness score
✅ Competency tracking per category
✅ Study session analytics
✅ Professional profile updates
✅ Recommended topics based on competencies
✅ Recent activity tracking
