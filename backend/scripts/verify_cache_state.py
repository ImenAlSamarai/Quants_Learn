"""
Verify cache state for Statistical Inference across all difficulty levels
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.database import SessionLocal, Node, GeneratedContent

def main():
    db = SessionLocal()

    # Get Statistical Inference node
    node = db.query(Node).filter(Node.title == 'Statistical Inference').first()

    if not node:
        print("❌ Statistical Inference node not found!")
        return

    print("=" * 80)
    print(f"Cache State for: {node.title} (ID: {node.id})")
    print("=" * 80)
    print()

    # Get all cached content for this node
    cached = db.query(GeneratedContent).filter(
        GeneratedContent.node_id == node.id
    ).all()

    if not cached:
        print("✅ NO CACHE - All difficulty levels will generate fresh content")
        print()
        return

    print(f"⚠️  Found {len(cached)} cached entries:\n")

    for entry in cached:
        print(f"Difficulty {entry.difficulty_level} - {entry.content_type}")
        print(f"  Created: {entry.created_at}")
        print(f"  Valid: {entry.is_valid}")

        # Check if it has Bouchaud content
        has_bouchaud = 'bouchaud' in entry.generated_content.lower()
        has_heavy_tail = 'heavy-tailed' in entry.generated_content.lower() or 'heavy tail' in entry.generated_content.lower()
        has_levy = 'lévy' in entry.generated_content.lower() or 'levy' in entry.generated_content.lower()

        print(f"  Contains Bouchaud concepts: ", end="")
        if has_bouchaud or has_heavy_tail or has_levy:
            print("✓ YES")
        else:
            print("✗ NO (OLD CONTENT)")
        print()

    print("=" * 80)
    print("\nTo clear all cache:")
    print(f"  python scripts/clear_generated_content_cache.py --node-id {node.id}")
    print()

    db.close()

if __name__ == "__main__":
    main()
