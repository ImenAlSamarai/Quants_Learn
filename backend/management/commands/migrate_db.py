"""
Database Migration Command

Safely applies Phase 2 + 2.5 schema changes:
- Phase 2: User profile fields (email, phone, cv_url, linkedin_url, education_level, job_role, years_experience, target_roles)
- Phase 2.5: Job-based personalization (job_title, job_description, job_seniority, firm, job_role_type)
- New tables: UserCompetency, StudySession, LearningPath
- GeneratedContent cache updates: role_template_id, job_profile_hash
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.models.database import SessionLocal, engine, Base, User, UserCompetency, StudySession, LearningPath, GeneratedContent
from sqlalchemy import inspect, text


class MigrateDatabaseCommand:
    """Migrate database to Phase 2.5 schema (job-based personalization)"""

    def __init__(self):
        self.db = None

    def run(self, dry_run=False):
        """Run database migration"""
        self.db = SessionLocal()

        try:
            print("=" * 80)
            print(" DATABASE MIGRATION: Phase 2.5 Job-Based Personalization")
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

            # Phase 2 + 2.5 changes needed
            changes_needed = []

            # Check if new tables exist
            if 'user_competencies' not in existing_tables:
                changes_needed.append("Create user_competencies table")

            if 'study_sessions' not in existing_tables:
                changes_needed.append("Create study_sessions table")

            if 'learning_paths' not in existing_tables:
                changes_needed.append("Create learning_paths table (Phase 2.5)")

            # Check if new User columns exist
            # CRITICAL: Query information_schema directly to avoid SQLAlchemy cache
            if 'users' in existing_tables:
                result = self.db.execute(text(
                    "SELECT column_name FROM information_schema.columns WHERE table_name = 'users'"
                ))
                user_columns = [row[0] for row in result.fetchall()]

                # Phase 2 columns
                phase2_columns = ['email', 'phone', 'cv_url', 'linkedin_url',
                                  'education_level', 'job_role', 'years_experience', 'target_roles']

                for col in phase2_columns:
                    if col not in user_columns:
                        changes_needed.append(f"Add users.{col} column (Phase 2)")

                # Phase 2.5 job-based personalization columns
                phase25_columns = ['job_title', 'job_description', 'job_seniority', 'firm', 'job_role_type']

                for col in phase25_columns:
                    if col not in user_columns:
                        changes_needed.append(f"Add users.{col} column (Phase 2.5 - Job-based)")

            # Check if GeneratedContent has new cache key columns
            # CRITICAL: Query information_schema directly to avoid SQLAlchemy cache
            if 'generated_content' in existing_tables:
                result = self.db.execute(text(
                    "SELECT column_name FROM information_schema.columns WHERE table_name = 'generated_content'"
                ))
                gc_columns = [row[0] for row in result.fetchall()]

                if 'role_template_id' not in gc_columns:
                    changes_needed.append("Add generated_content.role_template_id column (Phase 2.5 cache)")

                if 'job_profile_hash' not in gc_columns:
                    changes_needed.append("Add generated_content.job_profile_hash column (Phase 2.5 cache)")

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
            print("⚠️  NOTE: Hard cut migration - all cached content will be cleared")
            response = input("Proceed with migration? (yes/no): ")

            if response.lower() != 'yes':
                print("Migration cancelled")
                return 0

            # Apply migration
            print()
            print("Applying migration...")
            print()

            # Step 1: Create new tables (create_all only creates missing tables, not columns)
            Base.metadata.create_all(bind=engine)
            print("✓ New tables created")

            # Step 2: Add missing columns to existing tables using ALTER TABLE
            # This is the robust approach - SQLAlchemy's create_all() does NOT add columns!

            # IMPORTANT: Re-query columns directly from database to avoid inspector cache
            # SQLAlchemy inspector caches column metadata, so we query information_schema instead

            # Add Phase 2 columns to users table
            if 'users' in existing_tables:
                # Query actual columns from database (bypasses cache)
                result = self.db.execute(text(
                    "SELECT column_name FROM information_schema.columns WHERE table_name = 'users'"
                ))
                user_columns = [row[0] for row in result.fetchall()]

                phase2_column_defs = {
                    'email': 'VARCHAR(255)',
                    'phone': 'VARCHAR(50)',
                    'cv_url': 'TEXT',
                    'linkedin_url': 'TEXT',
                    'education_level': 'VARCHAR(100)',
                    'job_role': 'VARCHAR(200)',
                    'years_experience': 'INTEGER',
                    'target_roles': 'TEXT'
                }

                for col_name, col_type in phase2_column_defs.items():
                    if col_name not in user_columns:
                        self.db.execute(text(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}"))
                        print(f"  ✓ Added users.{col_name}")

                # Add Phase 2.5 job-based personalization columns
                phase25_column_defs = {
                    'job_title': 'VARCHAR(200)',
                    'job_description': 'TEXT',
                    'job_seniority': 'VARCHAR(50)',
                    'firm': 'VARCHAR(200)',
                    'job_role_type': 'VARCHAR(100)'
                }

                for col_name, col_type in phase25_column_defs.items():
                    if col_name not in user_columns:
                        self.db.execute(text(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}"))
                        print(f"  ✓ Added users.{col_name}")

                self.db.commit()

            # Add cache key columns to generated_content table
            if 'generated_content' in existing_tables:
                # Query actual columns from database (bypasses cache)
                result = self.db.execute(text(
                    "SELECT column_name FROM information_schema.columns WHERE table_name = 'generated_content'"
                ))
                gc_columns = [row[0] for row in result.fetchall()]

                # Make difficulty_level nullable first if it exists and isn't already
                if 'difficulty_level' in gc_columns:
                    try:
                        self.db.execute(text("ALTER TABLE generated_content ALTER COLUMN difficulty_level DROP NOT NULL"))
                        print("  ✓ Made difficulty_level nullable")
                    except Exception:
                        pass  # Already nullable

                # Add new cache key columns
                if 'role_template_id' not in gc_columns:
                    self.db.execute(text("ALTER TABLE generated_content ADD COLUMN role_template_id VARCHAR(50)"))
                    print("  ✓ Added generated_content.role_template_id")

                if 'job_profile_hash' not in gc_columns:
                    self.db.execute(text("ALTER TABLE generated_content ADD COLUMN job_profile_hash VARCHAR(32)"))
                    print("  ✓ Added generated_content.job_profile_hash")

                self.db.commit()

                # Create indexes for cache keys
                try:
                    self.db.execute(text("CREATE INDEX IF NOT EXISTS ix_generated_content_role_template_id ON generated_content(role_template_id)"))
                    self.db.execute(text("CREATE INDEX IF NOT EXISTS ix_generated_content_job_profile_hash ON generated_content(job_profile_hash)"))
                    self.db.commit()
                    print("  ✓ Created indexes on cache key columns")
                except Exception as e:
                    print(f"  ⚠️  Index creation skipped: {e}")

            print("✓ Schema updated")

            # Clear all cached content (Hard cut migration)
            print()
            print("Clearing cached content (hard cut migration)...")
            try:
                deleted_count = self.db.query(GeneratedContent).delete()
                self.db.commit()
                print(f"✓ Cleared {deleted_count} cached content entries")
            except Exception as e:
                print(f"⚠️  Warning: Could not clear cache - {e}")
                self.db.rollback()

            # Verify migration
            # Force SQLAlchemy to clear its metadata cache
            engine.dispose()
            inspector = inspect(engine)
            new_tables = inspector.get_table_names()

            print()
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

            # Verify LearningPath table was created
            if 'learning_paths' in new_tables:
                lp_columns = [col['name'] for col in inspector.get_columns('learning_paths')]
                print("✓ LearningPath table created with columns:")
                for col in lp_columns:
                    print(f"    • {col}")
                print()

            print("=" * 80)
            print(" MIGRATION SUCCESSFUL")
            print("=" * 80)
            print()
            print("Phase 2.5 Job-Based Personalization is now active!")
            print()
            print("Next steps:")
            print("  1. Restart your server: uvicorn app.main:app --reload")
            print("  2. Test new endpoints:")
            print("     POST /api/users/{user_id}/job-profile")
            print("     GET  /api/users/{user_id}/learning-path")
            print("     POST /api/users/check-coverage")
            print("  3. Users will need to set their job profiles in settings")
            print("  4. Content will be regenerated with job-based personalization")
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
