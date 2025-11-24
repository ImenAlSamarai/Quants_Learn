#!/usr/bin/env python3
"""
Clear cached generated content to force regeneration with new prompts
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models.database import SessionLocal, GeneratedContent
from sqlalchemy import func


def clear_all_cache():
    """Clear all cached generated content"""
    db = SessionLocal()
    try:
        count = db.query(GeneratedContent).count()
        print(f"Found {count} cached content entries")

        if count > 0:
            confirm = input(f"Delete all {count} cached entries? (yes/no): ")
            if confirm.lower() == 'yes':
                db.query(GeneratedContent).delete()
                db.commit()
                print(f"✓ Deleted all {count} cached entries")
            else:
                print("Cancelled")
        else:
            print("No cached content found")
    finally:
        db.close()


def clear_cache_by_node(node_id: int):
    """Clear cached content for a specific node"""
    db = SessionLocal()
    try:
        count = db.query(GeneratedContent).filter(
            GeneratedContent.node_id == node_id
        ).count()

        if count > 0:
            db.query(GeneratedContent).filter(
                GeneratedContent.node_id == node_id
            ).delete()
            db.commit()
            print(f"✓ Deleted {count} cached entries for node {node_id}")
        else:
            print(f"No cached content found for node {node_id}")
    finally:
        db.close()


def clear_cache_by_difficulty(difficulty_level: int):
    """Clear cached content for a specific difficulty level"""
    db = SessionLocal()
    try:
        count = db.query(GeneratedContent).filter(
            GeneratedContent.difficulty_level == difficulty_level
        ).count()

        if count > 0:
            db.query(GeneratedContent).filter(
                GeneratedContent.difficulty_level == difficulty_level
            ).delete()
            db.commit()
            print(f"✓ Deleted {count} cached entries for difficulty level {difficulty_level}")
        else:
            print(f"No cached content found for difficulty level {difficulty_level}")
    finally:
        db.close()


def show_cache_stats():
    """Show statistics about cached content"""
    db = SessionLocal()
    try:
        total = db.query(GeneratedContent).count()
        print(f"\n📊 Cache Statistics:")
        print(f"Total cached entries: {total}")

        # By content type
        print("\nBy content type:")
        types = db.query(
            GeneratedContent.content_type,
            func.count(GeneratedContent.id)
        ).group_by(GeneratedContent.content_type).all()
        for content_type, count in types:
            print(f"  - {content_type}: {count}")

        # By difficulty level
        print("\nBy difficulty level:")
        difficulties = db.query(
            GeneratedContent.difficulty_level,
            func.count(GeneratedContent.id)
        ).group_by(GeneratedContent.difficulty_level).all()
        for difficulty, count in difficulties:
            print(f"  - Level {difficulty}: {count}")

        # Most accessed
        print("\nMost accessed content:")
        top_accessed = db.query(GeneratedContent).order_by(
            GeneratedContent.access_count.desc()
        ).limit(5).all()
        for entry in top_accessed:
            print(f"  - Node {entry.node_id} ({entry.content_type}, difficulty {entry.difficulty_level}): {entry.access_count} accesses")
    finally:
        db.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Manage cached generated content")
    parser.add_argument('action', choices=['clear-all', 'clear-node', 'clear-difficulty', 'stats'],
                       help='Action to perform')
    parser.add_argument('--node-id', type=int, help='Node ID (for clear-node)')
    parser.add_argument('--difficulty', type=int, choices=[1, 2, 3, 4, 5],
                       help='Difficulty level (for clear-difficulty)')

    args = parser.parse_args()

    if args.action == 'clear-all':
        clear_all_cache()
    elif args.action == 'clear-node':
        if not args.node_id:
            print("Error: --node-id required for clear-node action")
            sys.exit(1)
        clear_cache_by_node(args.node_id)
    elif args.action == 'clear-difficulty':
        if not args.difficulty:
            print("Error: --difficulty required for clear-difficulty action")
            sys.exit(1)
        clear_cache_by_difficulty(args.difficulty)
    elif args.action == 'stats':
        show_cache_stats()
