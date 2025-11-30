"""
Initialize database tables without requiring API keys

This script creates all database tables including the new TopicStructure table.
It bypasses the settings validation to allow database initialization without API keys.
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set dummy environment variables to satisfy pydantic validation
os.environ['PINECONE_API_KEY'] = 'dummy'
os.environ['OPENAI_API_KEY'] = 'dummy'

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.database import Base, User, TopicStructure

# Use default database URL or from environment
# Try PostgreSQL first, fall back to SQLite if PostgreSQL isn't available
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/quant_learn')

# Try to connect to PostgreSQL, fall back to SQLite if it fails
try:
    print(f"🔧 Trying to connect to PostgreSQL at: {DATABASE_URL}")
    engine = create_engine(DATABASE_URL)
    # Test connection
    with engine.connect() as conn:
        pass
    print("✅ Connected to PostgreSQL")
except Exception as e:
    print(f"⚠️  PostgreSQL not available: {e}")
    # Fall back to SQLite
    sqlite_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'quant_learn.db')
    DATABASE_URL = f'sqlite:///{sqlite_path}'
    print(f"🔧 Using SQLite instead at: {DATABASE_URL}")
    engine = create_engine(DATABASE_URL)

# Create all tables
print("📦 Creating all tables...")
Base.metadata.create_all(bind=engine)

print("✅ Database initialized successfully!")
print("\nCreated tables:")
print("  - nodes")
print("  - content_chunks")
print("  - users")
print("  - user_progress")
print("  - generated_content")
print("  - topic_insights")
print("  - user_competencies")
print("  - study_sessions")
print("  - learning_paths")
print("  - topic_structures (for caching learning structures)")
print("  - section_contents (NEW - for caching rich section content)")
print("\n💡 Smart Caching System:")
print("  TopicStructure: Learning roadmaps (weeks/sections)")
print("    - First generation: ~$0.006 with gpt-4o-mini")
print("    - Cached retrievals: FREE!")
print("  SectionContent: Rich learning content with Claude")
print("    - First generation: ~$0.02-0.05 with Claude Sonnet 3.5")
print("    - Cached retrievals: FREE!")
print("    - Premium quality matching 'statistical modeling' example")
