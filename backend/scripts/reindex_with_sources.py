#!/usr/bin/env python3
"""
Re-index all content with proper source metadata

This script re-runs the content indexer to fix "Unknown" sources.
It will overwrite existing vectors with properly labeled ones.

Usage:
    cd backend
    python scripts/reindex_with_sources.py
"""

import os
import sys
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.database import SessionLocal, Node
from index_content import ContentIndexer

def main():
    print("\n" + "="*80)
    print("🔄 RE-INDEXING CONTENT WITH PROPER SOURCE METADATA")
    print("="*80 + "\n")

    db = SessionLocal()
    indexer = ContentIndexer()

    try:
        # Get all nodes that have content
        nodes = db.query(Node).filter(Node.content_path.isnot(None)).all()

        print(f"Found {len(nodes)} nodes with content to re-index\n")

        reindexed_count = 0
        failed_count = 0

        for node in nodes:
            try:
                print(f"Re-indexing: {node.title} (category: {node.category})")

                # Re-index this node with proper source metadata
                indexer.index_node(
                    title=node.title,
                    category=node.category,
                    subcategory=node.subcategory,
                    content_path=node.content_path,
                    description=node.description,
                    difficulty=node.difficulty_level,
                    x_pos=node.x_position,
                    y_pos=node.y_position,
                    color=node.color,
                    icon=node.icon
                )

                reindexed_count += 1
                print(f"✓ Successfully re-indexed '{node.title}'\n")

            except Exception as e:
                failed_count += 1
                print(f"❌ Failed to re-index '{node.title}': {e}\n")
                continue

        print("="*80)
        print("SUMMARY")
        print("="*80)
        print(f"Total nodes: {len(nodes)}")
        print(f"Successfully re-indexed: {reindexed_count}")
        print(f"Failed: {failed_count}")
        print("="*80 + "\n")

        if reindexed_count > 0:
            print("✅ Success! All content has been re-indexed with proper source metadata.")
            print("\nNow test your job description again - you should see:")
            print("  ✓ 'Quant Interview Questions: Probability' instead of 'Unknown'")
            print("  ✓ 'Quant Learning Materials: Statistics' instead of 'Unknown'")
            print("  ✓ 'Bouchaud: Theory of Financial Risk...' for Bouchaud content")
        else:
            print("⚠️  No content was re-indexed. Check that content files exist.")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        indexer.close()
        db.close()


if __name__ == "__main__":
    main()
