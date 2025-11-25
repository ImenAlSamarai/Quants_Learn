"""
Database migration for job-based personalization system

Migrates from difficulty-based (learning_level 1-5) to job-based personalization.

Strategy: Hard cut for beta
- Add new columns to users table (job fields)
- Modify generated_content table (cache keys)
- Create new learning_paths table
- Delete all cached content (fresh start)

Usage:
    python backend/manage.py migrate_to_job_based
"""

from app.models.database import SessionLocal, Base, engine, GeneratedContent
from sqlalchemy import text
import sys


def run():
    """Execute database migration"""

    print("=" * 60)
    print("JOB-BASED PERSONALIZATION MIGRATION")
    print("=" * 60)
    print("\nThis migration will:")
    print("  1. Add job personalization fields to users table")
    print("  2. Modify generated_content cache strategy")
    print("  3. Create learning_paths table")
    print("  4. DELETE all cached content (hard cut)")
    print("\nWARNING: Users will need to re-set preferences in new UI")
    print("=" * 60)

    response = input("\nContinue? (yes/no): ")
    if response.lower() != 'yes':
        print("Migration cancelled.")
        sys.exit(0)

    db = SessionLocal()

    try:
        print("\n🔄 Starting migration...\n")

        # Step 1: Add new columns to users table
        print("Step 1: Adding job fields to users table...")

        try:
            db.execute(text("""
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS job_title VARCHAR(200),
                ADD COLUMN IF NOT EXISTS job_description TEXT,
                ADD COLUMN IF NOT EXISTS job_seniority VARCHAR(50),
                ADD COLUMN IF NOT EXISTS firm VARCHAR(200),
                ADD COLUMN IF NOT EXISTS job_role_type VARCHAR(100);
            """))
            db.commit()
            print("  ✓ Job fields added to users table")
        except Exception as e:
            print(f"  ⚠️  Error adding columns (may already exist): {e}")
            db.rollback()

        # Step 2: Modify generated_content table
        print("\nStep 2: Updating generated_content cache strategy...")

        try:
            # Make difficulty_level nullable
            db.execute(text("""
                ALTER TABLE generated_content
                ALTER COLUMN difficulty_level DROP NOT NULL;
            """))

            # Add new cache key columns
            db.execute(text("""
                ALTER TABLE generated_content
                ADD COLUMN IF NOT EXISTS role_template_id VARCHAR(50),
                ADD COLUMN IF NOT EXISTS job_profile_hash VARCHAR(32);
            """))

            # Add indexes
            db.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_role_template
                ON generated_content(role_template_id);
            """))

            db.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_job_hash
                ON generated_content(job_profile_hash);
            """))

            db.commit()
            print("  ✓ Generated_content table updated with new cache keys")
        except Exception as e:
            print(f"  ⚠️  Error modifying generated_content: {e}")
            db.rollback()

        # Step 3: Create learning_paths table
        print("\nStep 3: Creating learning_paths table...")

        try:
            # Check if table already exists
            result = db.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_name = 'learning_paths'
                );
            """))

            table_exists = result.scalar()

            if not table_exists:
                # Use SQLAlchemy to create table (ensures consistency with model)
                from app.models.database import LearningPath
                Base.metadata.create_all(bind=engine, tables=[LearningPath.__table__])
                print("  ✓ Learning_paths table created")
            else:
                print("  ⚠️  Learning_paths table already exists, skipping...")
        except Exception as e:
            print(f"  ✗ Error creating learning_paths table: {e}")
            db.rollback()

        # Step 4: HARD CUT - Delete old cached content
        print("\nStep 4: Clearing old cached content (hard cut)...")

        try:
            # Count before deletion
            count_before = db.query(GeneratedContent).count()
            print(f"  Current cached items: {count_before}")

            if count_before > 0:
                confirm = input(f"  DELETE {count_before} cached items? (yes/no): ")
                if confirm.lower() == 'yes':
                    deleted = db.query(GeneratedContent).delete()
                    db.commit()
                    print(f"  ✓ Deleted {deleted} cached explanations")
                else:
                    print("  Skipped cache deletion")
            else:
                print("  No cached content to delete")
        except Exception as e:
            print(f"  ✗ Error deleting cached content: {e}")
            db.rollback()

        # Step 5: Verify migration
        print("\nStep 5: Verifying migration...")

        try:
            # Check users table columns
            result = db.execute(text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'users'
                AND column_name IN ('job_title', 'job_description', 'job_seniority', 'firm', 'job_role_type');
            """))

            columns = [row[0] for row in result]
            print(f"  ✓ Users table has {len(columns)}/5 job fields")

            # Check learning_paths table exists
            result = db.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_name = 'learning_paths'
                );
            """))

            if result.scalar():
                print("  ✓ Learning_paths table exists")
            else:
                print("  ✗ Learning_paths table not found!")

            # Check generated_content columns
            result = db.execute(text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'generated_content'
                AND column_name IN ('role_template_id', 'job_profile_hash');
            """))

            cache_columns = [row[0] for row in result]
            print(f"  ✓ Generated_content has {len(cache_columns)}/2 new cache key fields")

        except Exception as e:
            print(f"  ⚠️  Verification error: {e}")

        print("\n" + "=" * 60)
        print("✅ MIGRATION COMPLETE!")
        print("=" * 60)
        print("\nNext steps:")
        print("  1. Users will need to set job preferences in new UI")
        print("  2. Content will regenerate on-demand with job context")
        print("  3. Learning paths will be auto-generated for each user")
        print("\nBackward compatibility:")
        print("  - learning_level field still exists (for scripts)")
        print("  - Old difficulty-based methods still work")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    run()
