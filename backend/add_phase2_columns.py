#!/usr/bin/env python3
"""
Add Phase 2 columns to users table
This script bypasses the Pydantic settings to avoid requiring API keys
"""
import os
from sqlalchemy import create_engine, text

# Get database URL from environment or use default
DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'postgresql://postgres:postgres@localhost:5432/quant_learn'
)

print(f"🔧 Connecting to database...")
engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as conn:
        print(f"✅ Connected successfully!")
        print(f"📝 Adding Phase 2 columns to users table...")

        # Add each column with IF NOT EXISTS to make it idempotent
        columns = [
            'ALTER TABLE users ADD COLUMN IF NOT EXISTS email VARCHAR(200)',
            'ALTER TABLE users ADD COLUMN IF NOT EXISTS phone VARCHAR(50)',
            'ALTER TABLE users ADD COLUMN IF NOT EXISTS cv_url VARCHAR(500)',
            'ALTER TABLE users ADD COLUMN IF NOT EXISTS linkedin_url VARCHAR(500)',
            'ALTER TABLE users ADD COLUMN IF NOT EXISTS education_level VARCHAR(50)',
            'ALTER TABLE users ADD COLUMN IF NOT EXISTS "current_role" VARCHAR(200)',  # Quoted: reserved keyword
            'ALTER TABLE users ADD COLUMN IF NOT EXISTS years_experience INTEGER',
            'ALTER TABLE users ADD COLUMN IF NOT EXISTS target_roles JSON',
        ]

        for sql in columns:
            conn.execute(text(sql))
            print(f"   ✓ {sql.split('ADD COLUMN IF NOT EXISTS')[1].split()[0]}")

        conn.commit()
        print(f"\n✅ All Phase 2 columns added successfully!")
        print(f"🚀 You can now start the backend server.")

except Exception as e:
    print(f"\n❌ Error: {e}")
    print(f"\n💡 If PostgreSQL is not running, you may need to:")
    print(f"   1. Start PostgreSQL service")
    print(f"   2. Or adjust DATABASE_URL environment variable")
    raise
