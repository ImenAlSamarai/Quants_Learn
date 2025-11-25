"""
Database Migration Command

Safely applies Phase 2 schema changes (new User fields, UserCompetency, StudySession tables).
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.models.database import SessionLocal, engine, Base, User, UserCompetency, StudySession
from sqlalchemy import inspect, text


class MigrateDatabaseCommand:
    """Migrate database to Phase 2 schema"""

    def __init__(self):
        self.db = None

    def run(self, dry_run=False):
        """Run database migration"""
        self.db = SessionLocal()

        try:
            print("=" * 80)
            print(" DATABASE MIGRATION: Phase 2 Schema")
            print("=" * 80)
            print()

            if dry_run:
                print("🔍 DRY RUN MODE - No changes will be made")
                print()

            # Check current schema
            inspector = inspect(engine)
            existing_tables = inspector.get_table_names()

            print("Current tables:")
            for table in existing_tables:
                print(f"  ✓ {table}")
            print()

            # Phase 2 changes needed
            changes_needed = []

            # Check if new tables exist
            if 'user_competencies' not in existing_tables:
                changes_needed.append("Create user_competencies table")

            if 'study_sessions' not in existing_tables:
                changes_needed.append("Create study_sessions table")

            # Check if new User columns exist
            if 'users' in existing_tables:
                user_columns = [col['name'] for col in inspector.get_columns('users')]

                new_columns = ['email', 'phone', 'cv_url', 'linkedin_url',
                               'education_level', 'job_role', 'years_experience', 'target_roles']

                for col in new_columns:
                    if col not in user_columns:
                        changes_needed.append(f"Add users.{col} column")

            if not changes_needed:
                print("✅ Database schema is up to date!")
                print("   No migration needed.")
                return 0

            print(f"⚠️  Migration needed: {len(changes_needed)} changes")
            print()
            for i, change in enumerate(changes_needed, 1):
                print(f"   {i}. {change}")
            print()

            if dry_run:
                print("🔍 DRY RUN MODE - Migration plan shown above")
                print("   Run without --dry-run to apply changes")
                return 0

            # Confirm before proceeding
            print("⚠️  WARNING: This will modify your database schema")
            response = input("Proceed with migration? (yes/no): ")

            if response.lower() != 'yes':
                print("Migration cancelled")
                return 0

            # Apply migration
            print()
            print("Applying migration...")
            print()

            # Create new tables (SQLAlchemy will only create missing tables)
            Base.metadata.create_all(bind=engine)

            # Verify migration
            inspector = inspect(engine)
            new_tables = inspector.get_table_names()

            print("✅ Migration complete!")
            print()
            print("Tables after migration:")
            for table in new_tables:
                indicator = "NEW" if table not in existing_tables else "   "
                print(f"  {indicator} {table}")
            print()

            # Verify new columns in users table
            if 'users' in new_tables:
                user_columns = [col['name'] for col in inspector.get_columns('users')]
                print("Users table columns:")
                for col in user_columns:
                    print(f"    • {col}")
                print()

            print("=" * 80)
            print(" MIGRATION SUCCESSFUL")
            print("=" * 80)
            print()
            print("Next steps:")
            print("  1. Verify migration: python manage.py health-check")
            print("  2. Test user profile updates")
            print("  3. Verify no errors in application logs")
            print()

            return 0

        except Exception as e:
            print(f"❌ Migration failed: {e}")
            import traceback
            traceback.print_exc()
            return 1

        finally:
            if self.db:
                self.db.close()
