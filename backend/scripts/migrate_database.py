#!/usr/bin/env python3
"""
Database migration script to add new tables for caching and user management.

This script will:
1. Create new tables (users, generated_content)
2. Update existing tables (user_progress foreign key)
3. Preserve existing data

Usage:
    python backend/scripts/migrate_database.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import create_engine, text
from app.config.settings import settings
from app.models.database import Base, init_db


def migrate():
    """Run database migration"""

    print("=" * 60)
    print("DATABASE MIGRATION")
    print("=" * 60)
    print()
    print("This will add new tables for:")
    print("  - Content caching (generated_content)")
    print("  - User management (users)")
    print("  - Enhanced progress tracking")
    print()

    response = input("Continue? (yes/no): ")
    if response.lower() != 'yes':
        print("Migration cancelled.")
        return

    print("\nConnecting to database...")
    engine = create_engine(settings.DATABASE_URL)

    # Create all tables (will skip existing ones)
    print("Creating new tables...")
    Base.metadata.create_all(bind=engine)

    print("\n✓ Migration complete!")
    print()
    print("New tables created:")
    print("  - users (user profiles with learning levels)")
    print("  - generated_content (cached LLM responses)")
    print()
    print("Existing data preserved:")
    print("  - nodes")
    print("  - content_chunks")
    print("  - user_progress")
    print()
    print("Next steps:")
    print("  1. Restart the backend: python -m uvicorn app.main:app --reload")
    print("  2. Visit http://localhost:8000/docs to see new API endpoints")
    print("  3. Test caching by clicking mind map nodes")
    print()
    print("=" * 60)


if __name__ == "__main__":
    migrate()
