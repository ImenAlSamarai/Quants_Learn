"""
Update Learning Paths from Configuration

Reads app/config/learning_paths.yaml and updates Node metadata.
Safe to run multiple times (idempotent).

Usage:
    python scripts/update_learning_paths.py [--dry-run]

Options:
    --dry-run    Show what would be updated without making changes
"""

import os
import sys
from pathlib import Path

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yaml
from sqlalchemy.orm import Session
from app.models.database import SessionLocal, Node


def load_config():
    """Load learning paths configuration from YAML"""
    config_path = Path(__file__).parent.parent / "app" / "config" / "learning_paths.yaml"

    if not config_path.exists():
        print(f"❌ Config file not found: {config_path}")
        sys.exit(1)

    with open(config_path, 'r') as f:
        try:
            config = yaml.safe_load(f)
            return config
        except yaml.YAMLError as e:
            print(f"❌ Error parsing YAML: {e}")
            sys.exit(1)


def update_learning_paths(dry_run=False):
    """Update node metadata from configuration"""

    config = load_config()
    db = SessionLocal()

    print("=" * 80)
    print("Learning Paths Update")
    print("=" * 80)
    if dry_run:
        print("🔍 DRY RUN MODE - No changes will be made")
    print()

    paths_data = config.get('paths', {})

    # Statistics
    stats = {
        'updated': 0,
        'not_found': 0,
        'errors': 0
    }

    not_found_topics = []

    try:
        for path_key, path_info in paths_data.items():
            path_name = path_info.get('name', path_key)
            topics = path_info.get('topics', [])

            print(f"\n📂 Processing path: {path_name}")
            print(f"   Topics: {len(topics)}")

            for topic_data in topics:
                title = topic_data.get('title')

                if not title:
                    print(f"   ⚠️  Skipping topic with no title")
                    continue

                # Find node by exact title match
                node = db.query(Node).filter(Node.title == title).first()

                if not node:
                    print(f"   ❌ Not found: {title}")
                    not_found_topics.append(title)
                    stats['not_found'] += 1
                    continue

                # Update metadata
                try:
                    node.learning_path = path_key
                    node.sequence_order = topic_data.get('sequence')
                    node.tags = topic_data.get('tags', [])

                    # Resolve prerequisites (title → node ID)
                    prereq_titles = topic_data.get('prerequisites', [])
                    prereq_ids = []

                    for prereq_title in prereq_titles:
                        prereq_node = db.query(Node).filter(Node.title == prereq_title).first()
                        if prereq_node:
                            prereq_ids.append(prereq_node.id)
                        else:
                            print(f"   ⚠️  Prerequisite not found: {prereq_title} (for {title})")

                    node.prerequisites_ids = prereq_ids

                    if not dry_run:
                        db.commit()

                    prereq_str = f" (prereqs: {len(prereq_ids)})" if prereq_ids else ""
                    print(f"   ✓ {title}{prereq_str}")
                    stats['updated'] += 1

                except Exception as e:
                    print(f"   ❌ Error updating {title}: {e}")
                    stats['errors'] += 1
                    db.rollback()

        if not dry_run:
            db.commit()

        # Summary
        print("\n" + "=" * 80)
        print("Summary")
        print("=" * 80)
        print(f"✓ Updated: {stats['updated']} topics")

        if stats['not_found'] > 0:
            print(f"⚠️  Not found: {stats['not_found']} topics")
            print("\nTopics not found in database:")
            for topic in not_found_topics:
                print(f"  - {topic}")
            print("\n💡 These topics may not be indexed yet. Index them first, then run this script.")

        if stats['errors'] > 0:
            print(f"❌ Errors: {stats['errors']} topics")

        if not dry_run and stats['updated'] > 0:
            print("\n✅ Learning paths updated successfully!")
            print("\nNext steps:")
            print("  1. Restart backend: uvicorn app.main:app --reload")
            print("  2. Check Study Mode in frontend - topics should be grouped by learning path")
        elif dry_run:
            print("\n💡 Run without --dry-run to apply changes")

    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()

    finally:
        db.close()


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Update learning paths from config")
    parser.add_argument('--dry-run', action='store_true', help='Show changes without applying them')
    args = parser.parse_args()

    update_learning_paths(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
