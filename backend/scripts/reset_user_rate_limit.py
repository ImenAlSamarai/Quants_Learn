#!/usr/bin/env python3
"""
Reset rate limit for a user by deleting their learning paths.
This allows them to generate a new learning path immediately.

Usage:
    python scripts/reset_user_rate_limit.py <user_email>
    python scripts/reset_user_rate_limit.py --all  # Delete all learning paths (use with caution!)
"""

import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models.database import get_db, LearningPath, User
from sqlalchemy.orm import Session


def reset_user_rate_limit(user_id: str, db: Session):
    """Delete all learning paths for a user to reset their rate limit"""

    # Check if user exists
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        print(f"❌ User '{user_id}' not found in database")
        return False

    # Get all learning paths for this user
    learning_paths = db.query(LearningPath).filter(
        LearningPath.user_id == user_id
    ).all()

    if not learning_paths:
        print(f"ℹ️  User '{user_id}' has no learning paths. Rate limit already clear.")
        return True

    print(f"Found {len(learning_paths)} learning path(s) for user '{user_id}':")
    for i, path in enumerate(learning_paths, 1):
        print(f"  {i}. Created: {path.created_at} | Role: {path.role_type} | Coverage: {path.coverage_percentage}%")

    # Confirm deletion
    response = input(f"\n⚠️  Delete {len(learning_paths)} learning path(s) for '{user_id}'? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("❌ Cancelled. No changes made.")
        return False

    # Delete all learning paths
    for path in learning_paths:
        db.delete(path)

    db.commit()
    print(f"✅ Deleted {len(learning_paths)} learning path(s) for '{user_id}'")
    print(f"✅ Rate limit reset! User can now generate a new learning path immediately.")
    return True


def reset_all_rate_limits(db: Session):
    """Delete ALL learning paths (use with caution!)"""

    all_paths = db.query(LearningPath).all()

    if not all_paths:
        print("ℹ️  No learning paths found in database.")
        return True

    print(f"Found {len(all_paths)} total learning paths in database")

    # Show summary by user
    from collections import defaultdict
    paths_by_user = defaultdict(list)
    for path in all_paths:
        paths_by_user[path.user_id].append(path)

    print(f"\nBreakdown by user:")
    for user_id, paths in paths_by_user.items():
        print(f"  - {user_id}: {len(paths)} path(s)")

    # Confirm deletion
    response = input(f"\n⚠️  DELETE ALL {len(all_paths)} learning paths? This cannot be undone! (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("❌ Cancelled. No changes made.")
        return False

    # Delete all
    db.query(LearningPath).delete()
    db.commit()

    print(f"✅ Deleted ALL {len(all_paths)} learning paths")
    print(f"✅ All rate limits reset!")
    return True


def main():
    """Main entry point"""

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python scripts/reset_user_rate_limit.py <user_email>")
        print("  python scripts/reset_user_rate_limit.py --all")
        sys.exit(1)

    target = sys.argv[1]

    # Get database session
    db = next(get_db())

    try:
        if target == "--all":
            print("="*80)
            print("🚨 RESET ALL RATE LIMITS (Delete all learning paths)")
            print("="*80)
            reset_all_rate_limits(db)
        else:
            print("="*80)
            print(f"🔄 RESET RATE LIMIT for user: {target}")
            print("="*80)
            reset_user_rate_limit(target, db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
