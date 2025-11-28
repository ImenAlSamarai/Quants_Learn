#!/usr/bin/env python3
"""
Test exactly what the migration detection sees
"""

import sys
sys.path.insert(0, '.')

from app.models.database import SessionLocal
from sqlalchemy import text

def test_detection():
    db = SessionLocal()

    print("=" * 80)
    print(" TESTING MIGRATION DETECTION QUERY")
    print("=" * 80)
    print()

    # This is EXACTLY what the migration script runs for detection
    print("Running: SELECT column_name FROM information_schema.columns WHERE table_name = 'users'")
    print()

    result = db.execute(text(
        "SELECT column_name FROM information_schema.columns WHERE table_name = 'users'"
    ))
    user_columns = [row[0] for row in result.fetchall()]

    print(f"Columns found: {len(user_columns)}")
    print(f"Columns: {user_columns}")
    print()

    # Check Phase 2.5 columns
    phase25_columns = ['job_title', 'job_description', 'job_seniority', 'firm', 'job_role_type']

    print("Checking Phase 2.5 columns:")
    changes_needed = []
    for col in phase25_columns:
        if col not in user_columns:
            changes_needed.append(f"Add users.{col} column (Phase 2.5 - Job-based)")
            print(f"  ✗ {col} MISSING → will add")
        else:
            print(f"  ✓ {col} EXISTS → skip")

    print()
    print(f"Total changes needed: {len(changes_needed)}")
    if changes_needed:
        for i, change in enumerate(changes_needed, 1):
            print(f"  {i}. {change}")
    else:
        print("  No changes needed - database is up to date!")

    print()
    print("=" * 80)

    # Check generated_content too
    print()
    print("Running: SELECT column_name FROM information_schema.columns WHERE table_name = 'generated_content'")
    print()

    result = db.execute(text(
        "SELECT column_name FROM information_schema.columns WHERE table_name = 'generated_content'"
    ))
    gc_columns = [row[0] for row in result.fetchall()]

    print(f"Columns found: {len(gc_columns)}")
    print(f"Columns: {gc_columns}")
    print()

    cache_columns = ['role_template_id', 'job_profile_hash']
    print("Checking cache key columns:")
    for col in cache_columns:
        if col not in gc_columns:
            print(f"  ✗ {col} MISSING → will add")
        else:
            print(f"  ✓ {col} EXISTS → skip")

    print()
    print("=" * 80)

    db.close()

if __name__ == '__main__':
    test_detection()
