#!/usr/bin/env python3
"""
Diagnostic script to check actual database schema
"""

import sys
sys.path.insert(0, '.')

from app.models.database import SessionLocal, engine
from sqlalchemy import inspect, text

def diagnose():
    db = SessionLocal()
    inspector = inspect(engine)

    print("=" * 80)
    print(" DATABASE SCHEMA DIAGNOSTIC")
    print("=" * 80)
    print()

    # Check users table columns
    print("1. USERS TABLE - Checking Phase 2.5 columns:")
    print("-" * 80)

    if 'users' in inspector.get_table_names():
        user_columns = [col['name'] for col in inspector.get_columns('users')]
        print(f"Total columns via inspector: {len(user_columns)}")
        print()

        # Check Phase 2.5 job-based columns
        phase25_columns = ['job_title', 'job_description', 'job_seniority', 'firm', 'job_role_type']

        print("Phase 2.5 Columns (via SQLAlchemy inspector - MAY BE CACHED):")
        for col in phase25_columns:
            if col in user_columns:
                print(f"  ✓ {col} EXISTS (cached?)")
            else:
                print(f"  ✗ {col} MISSING")
        print()

        # Try direct SQL query to verify - THIS IS THE TRUTH
        print("ACTUAL DATABASE STATE (direct information_schema query):")
        try:
            # Get ALL columns from information_schema
            result = db.execute(text(
                "SELECT column_name FROM information_schema.columns WHERE table_name = 'users' ORDER BY ordinal_position"
            ))
            actual_columns = [row[0] for row in result.fetchall()]
            print(f"  Total columns in database: {len(actual_columns)}")
            print(f"  All columns: {', '.join(actual_columns)}")
            print()

            # Check Phase 2.5 specifically
            print("  Phase 2.5 columns in ACTUAL database:")
            for col in phase25_columns:
                if col in actual_columns:
                    print(f"    ✓ {col} EXISTS")
                else:
                    print(f"    ✗ {col} MISSING")
        except Exception as e:
            print(f"  Error querying information_schema: {e}")
        print()

    # Check generated_content table columns
    print("2. GENERATED_CONTENT TABLE - Checking cache key columns:")
    print("-" * 80)

    if 'generated_content' in inspector.get_table_names():
        gc_columns = [col['name'] for col in inspector.get_columns('generated_content')]
        print(f"Total columns in generated_content table: {len(gc_columns)}")
        print()

        cache_columns = ['role_template_id', 'job_profile_hash', 'difficulty_level']

        print("Cache Key Columns:")
        for col in cache_columns:
            if col in gc_columns:
                # Check if nullable
                col_info = next((c for c in inspector.get_columns('generated_content') if c['name'] == col), None)
                nullable = col_info['nullable'] if col_info else 'unknown'
                print(f"  ✓ {col} EXISTS (nullable={nullable})")
            else:
                print(f"  ✗ {col} MISSING")
        print()

    # Check learning_paths table
    print("3. LEARNING_PATHS TABLE:")
    print("-" * 80)

    if 'learning_paths' in inspector.get_table_names():
        lp_columns = [col['name'] for col in inspector.get_columns('learning_paths')]
        print(f"  ✓ Table EXISTS with {len(lp_columns)} columns")
        print(f"  Columns: {', '.join(lp_columns)}")
    else:
        print("  ✗ Table MISSING")
    print()

    # Check cached content count
    print("4. CACHED CONTENT:")
    print("-" * 80)
    try:
        result = db.execute(text("SELECT COUNT(*) FROM generated_content"))
        count = result.scalar()
        print(f"  Total cached content entries: {count}")

        if count > 0:
            result = db.execute(text("""
                SELECT
                    COUNT(CASE WHEN difficulty_level IS NOT NULL THEN 1 END) as difficulty_based,
                    COUNT(CASE WHEN role_template_id IS NOT NULL THEN 1 END) as template_based,
                    COUNT(CASE WHEN job_profile_hash IS NOT NULL THEN 1 END) as hash_based
                FROM generated_content
            """))
            stats = result.fetchone()
            print(f"    • Difficulty-based: {stats[0]}")
            print(f"    • Template-based: {stats[1]}")
            print(f"    • Hash-based: {stats[2]}")
    except Exception as e:
        print(f"  Error checking cache: {e}")
    print()

    # SQLAlchemy reflection cache check
    print("5. SQLALCHEMY REFLECTION CACHE:")
    print("-" * 80)
    print(f"  Engine: {engine.url}")
    print(f"  Dialect: {engine.dialect.name}")
    print(f"  Cached table names: {list(engine.dialect.get_table_names(engine.raw_connection()))}")
    print()

    print("=" * 80)
    print(" DIAGNOSIS COMPLETE")
    print("=" * 80)
    print()

    db.close()

if __name__ == '__main__':
    diagnose()
