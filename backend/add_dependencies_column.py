#!/usr/bin/env python3
"""
Add dependencies column to learning_paths table
This script bypasses the Pydantic settings to avoid requiring API keys
"""
import os
from pathlib import Path
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load .env file from backend directory
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

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
        print(f"📝 Adding dependencies column to learning_paths table...")

        # Add column with IF NOT EXISTS to make it idempotent
        sql = "ALTER TABLE learning_paths ADD COLUMN IF NOT EXISTS dependencies JSON DEFAULT '[]'"
        conn.execute(text(sql))
        print(f"   ✓ dependencies column added")

        conn.commit()
        print(f"\n✅ Dependencies column added successfully!")
        print(f"🚀 The tree visualization will now show dependency arrows.")

except Exception as e:
    print(f"\n❌ Error: {e}")
    print(f"\n💡 If PostgreSQL is not running, you may need to:")
    print(f"   1. Start PostgreSQL service")
    print(f"   2. Or adjust DATABASE_URL environment variable")
    raise
