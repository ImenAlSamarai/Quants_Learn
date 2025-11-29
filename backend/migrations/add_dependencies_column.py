"""
Migration: Add dependencies column to learning_paths table

This migration adds a JSON column to store topic dependencies (prerequisite relationships)
in the learning paths.

Run with: python -m backend.migrations.add_dependencies_column
"""

from sqlalchemy import create_engine, text
from backend.app.core.config import settings


def upgrade():
    """Add dependencies column to learning_paths table"""
    engine = create_engine(settings.DATABASE_URL)

    with engine.connect() as conn:
        # Check if column already exists
        result = conn.execute(text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name='learning_paths' AND column_name='dependencies'
        """))

        if result.fetchone() is None:
            # Add the column
            print("Adding dependencies column to learning_paths table...")
            conn.execute(text("""
                ALTER TABLE learning_paths
                ADD COLUMN dependencies JSON DEFAULT '[]'
            """))
            conn.commit()
            print("✓ Successfully added dependencies column")
        else:
            print("✓ Dependencies column already exists")


def downgrade():
    """Remove dependencies column from learning_paths table"""
    engine = create_engine(settings.DATABASE_URL)

    with engine.connect() as conn:
        print("Removing dependencies column from learning_paths table...")
        conn.execute(text("""
            ALTER TABLE learning_paths
            DROP COLUMN IF EXISTS dependencies
        """))
        conn.commit()
        print("✓ Successfully removed dependencies column")


if __name__ == "__main__":
    print("Running migration: add_dependencies_column")
    upgrade()
    print("Migration complete!")
