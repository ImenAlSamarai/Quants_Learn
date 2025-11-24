#!/usr/bin/env python3
"""
Clear Generated Content Cache

Clears cached LLM-generated content to force regeneration.
Useful after updating content chunks (e.g., adding Bouchaud Ch1).

Usage:
    python scripts/clear_generated_content_cache.py                    # Clear all cache
    python scripts/clear_generated_content_cache.py --node-id 17       # Clear specific node
    python scripts/clear_generated_content_cache.py --category stats   # Clear category
"""

import sys
import os
import argparse
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.database import SessionLocal, Node, GeneratedContent


def main():
    parser = argparse.ArgumentParser(description='Clear generated content cache')
    parser.add_argument('--node-id', type=int, help='Clear cache for specific node')
    parser.add_argument('--category', type=str, help='Clear cache for category')
    parser.add_argument('--all', action='store_true', help='Clear all cache')
    args = parser.parse_args()

    db = SessionLocal()

    try:
        print("=" * 80)
        print("Clear Generated Content Cache")
        print("=" * 80)
        print()

        # Determine what to clear
        if args.node_id:
            # Clear specific node
            node = db.query(Node).filter(Node.id == args.node_id).first()
            if not node:
                print(f"❌ Node {args.node_id} not found")
                return 1

            print(f"Clearing cache for: {node.title} (ID: {args.node_id})")
            print()

            cached_count = db.query(GeneratedContent).filter(
                GeneratedContent.node_id == args.node_id
            ).count()

            print(f"Found {cached_count} cached items")

            if cached_count > 0:
                response = input("Proceed with deletion? (y/n): ")
                if response.lower() != 'y':
                    print("Cancelled.")
                    return 0

                db.query(GeneratedContent).filter(
                    GeneratedContent.node_id == args.node_id
                ).delete()
                db.commit()
                print(f"✓ Deleted {cached_count} cached items")

        elif args.category:
            # Clear category
            print(f"Clearing cache for category: {args.category}")
            print()

            # Get all nodes in category
            nodes = db.query(Node).filter(Node.category.ilike(f'%{args.category}%')).all()
            node_ids = [n.id for n in nodes]

            if not node_ids:
                print(f"❌ No nodes found in category '{args.category}'")
                return 1

            print(f"Found {len(nodes)} nodes in category:")
            for node in nodes[:10]:  # Show first 10
                print(f"  • {node.title}")
            if len(nodes) > 10:
                print(f"  ... and {len(nodes) - 10} more")
            print()

            cached_count = db.query(GeneratedContent).filter(
                GeneratedContent.node_id.in_(node_ids)
            ).count()

            print(f"Found {cached_count} cached items")

            if cached_count > 0:
                response = input("Proceed with deletion? (y/n): ")
                if response.lower() != 'y':
                    print("Cancelled.")
                    return 0

                db.query(GeneratedContent).filter(
                    GeneratedContent.node_id.in_(node_ids)
                ).delete()
                db.commit()
                print(f"✓ Deleted {cached_count} cached items")

        elif args.all:
            # Clear all cache
            print("Clearing ALL cached content")
            print()

            total_count = db.query(GeneratedContent).count()
            print(f"Found {total_count} cached items")

            if total_count > 0:
                print()
                print("⚠️  WARNING: This will delete all cached content!")
                print("Generated content will need to be regenerated on next access.")
                print()
                response = input("Are you sure? (y/n): ")
                if response.lower() != 'y':
                    print("Cancelled.")
                    return 0

                db.query(GeneratedContent).delete()
                db.commit()
                print(f"✓ Deleted {total_count} cached items")

        else:
            # No option selected
            print("Please specify what to clear:")
            print("  --node-id 17          Clear specific node")
            print("  --category statistics Clear category")
            print("  --all                 Clear everything")
            print()
            print("Example: python scripts/clear_generated_content_cache.py --node-id 17")
            return 1

        print()
        print("=" * 80)
        print("Cache cleared successfully!")
        print("=" * 80)
        print()
        print("Next time users access this content, it will be regenerated")
        print("using the latest indexed chunks (including Bouchaud content).")

        return 0

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
