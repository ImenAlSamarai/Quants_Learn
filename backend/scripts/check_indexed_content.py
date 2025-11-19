"""
Check what content was actually indexed (works with any database)

Uses SQLAlchemy models instead of raw SQL
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.database import SessionLocal, Node, ContentChunk

def check_content():
    print("="*80)
    print("Indexed Content Check")
    print("="*80)
    print()

    db = SessionLocal()

    # Get ML nodes
    ml_nodes = db.query(Node).filter(Node.category == 'machine_learning').all()

    if not ml_nodes:
        print("❌ No Machine Learning nodes found!")
        db.close()
        return

    print(f"Found {len(ml_nodes)} Machine Learning nodes:")
    print("-"*80)
    print()

    total_chunks = 0

    for node in ml_nodes:
        # Get chunks for this node
        chunks = db.query(ContentChunk).filter(ContentChunk.node_id == node.id).all()
        chunk_count = len(chunks)
        total_chunks += chunk_count

        print(f"[{node.id}] {node.title}")
        print(f"     Chunks: {chunk_count}")

        if chunk_count > 0:
            # Calculate total characters
            total_chars = sum(len(c.chunk_text) for c in chunks)
            print(f"     Total chars: {total_chars:,}")

            # Show first chunk sample
            sample = chunks[0].chunk_text[:200].replace('\n', ' ')
            print(f"     Sample: {sample}...")
        else:
            print(f"     ❌ NO CONTENT - extraction failed!")

        print()

    print("="*80)
    print("Summary:")
    print("="*80)
    print(f"Total ML nodes: {len(ml_nodes)}")
    print(f"Total chunks: {total_chunks}")
    print()

    if total_chunks == 0:
        print("❌ PROBLEM: No content was indexed!")
        print("\nThis means section extraction is failing.")
        print("Run: python scripts/debug_sections.py")
        print("to see what sections actually exist in the PDF")
    elif total_chunks < 50:
        print("⚠️  WARNING: Very little content indexed")
        print(f"   Expected ~224 chunks, got {total_chunks}")
        print("\nMost sections weren't found.")
        print("Run: python scripts/debug_sections.py")
    else:
        print("✓ Good amount of content indexed!")

    db.close()


if __name__ == "__main__":
    check_content()
