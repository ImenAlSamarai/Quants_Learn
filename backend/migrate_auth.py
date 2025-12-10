"""
Migration script to add authentication fields to User table
Run this script to update the database schema for multi-role authentication
"""
from sqlalchemy import text
from app.models.database import engine

def migrate_auth_fields():
    """Add authentication and role-specific fields to users table"""
    migrations = [
        # Add authentication fields
        """
        ALTER TABLE users
        ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255);
        """,
        """
        ALTER TABLE users
        ADD COLUMN IF NOT EXISTS role VARCHAR(50) DEFAULT 'candidate';
        """,
        # Add candidate-specific fields
        """
        ALTER TABLE users
        ADD COLUMN IF NOT EXISTS cv_text TEXT;
        """,
        """
        ALTER TABLE users
        ADD COLUMN IF NOT EXISTS availability_date DATE;
        """,
        """
        ALTER TABLE users
        ADD COLUMN IF NOT EXISTS public_profile BOOLEAN DEFAULT FALSE;
        """,
        """
        ALTER TABLE users
        ADD COLUMN IF NOT EXISTS willing_to_relocate BOOLEAN;
        """,
        # Add recruiter-specific fields
        """
        ALTER TABLE users
        ADD COLUMN IF NOT EXISTS company_name VARCHAR(200);
        """,
        """
        ALTER TABLE users
        ADD COLUMN IF NOT EXISTS company_url VARCHAR(500);
        """,
        """
        ALTER TABLE users
        ADD COLUMN IF NOT EXISTS recruiter_type VARCHAR(50);
        """,
    ]

    with engine.connect() as conn:
        for migration_sql in migrations:
            try:
                conn.execute(text(migration_sql))
                conn.commit()
                print(f"✓ Executed: {migration_sql.strip()[:60]}...")
            except Exception as e:
                print(f"✗ Error: {str(e)[:100]}")
                print(f"  SQL: {migration_sql.strip()[:60]}...")

    print("\n✅ Migration completed!")
    print("Note: Existing users will have NULL password_hash and need to be updated manually or re-registered.")

if __name__ == "__main__":
    print("Starting authentication fields migration...\n")
    migrate_auth_fields()
