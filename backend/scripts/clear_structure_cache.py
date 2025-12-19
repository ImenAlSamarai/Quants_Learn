"""
Clear cached topic structures to force regeneration with new prompts

Run this after updating structure generation logic to ensure
all topics get regenerated with the latest improvements

Usage:
    cd backend
    python scripts/clear_structure_cache.py
"""
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.database import get_db, TopicStructure

def clear_cache():
    db = next(get_db())

    count = db.query(TopicStructure).count()
    print(f"Found {count} cached topic structures")

    if count > 0:
        confirm = input(f"Delete all {count} cached structures? (yes/no): ")
        if confirm.lower() == 'yes':
            db.query(TopicStructure).delete()
            db.commit()
            print(f"✅ Deleted {count} cached structures. Next generation will use new prompts!")
        else:
            print("Cancelled")
    else:
        print("No cached structures to delete")

if __name__ == "__main__":
    clear_cache()
