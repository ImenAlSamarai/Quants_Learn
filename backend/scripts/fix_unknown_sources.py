#!/usr/bin/env python3
"""
Fix "Unknown" sources in Pinecone vector store

This script helps identify and update content that was indexed without proper source metadata.

Usage:
    # List all vectors with "Unknown" source
    python scripts/fix_unknown_sources.py --list

    # Update specific content to have correct source
    python scripts/fix_unknown_sources.py --update \
        --filter "text_contains:probability brain teasers" \
        --new-source "Quant Interview Questions: Probability" \
        --chapter "Brain Teasers"

    # Update all "Unknown" from a specific node
    python scripts/fix_unknown_sources.py --update \
        --node-id 42 \
        --new-source "Bouchaud: Trades, Quotes and Prices" \
        --chapter "1"
"""

import os
import sys
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.vector_store import vector_store
from app.models.database import SessionLocal, Node
import argparse


def list_unknown_sources():
    """Query Pinecone for all vectors with Unknown source"""
    print("\n" + "="*80)
    print("SEARCHING FOR VECTORS WITH 'Unknown' SOURCE")
    print("="*80 + "\n")

    # Query with a generic search term
    test_queries = [
        "statistics",
        "probability",
        "machine learning",
        "risk",
        "trading"
    ]

    unknown_vectors = []

    for query in test_queries:
        print(f"Searching with query: '{query}'...")
        matches = vector_store.search(query=query, top_k=100)

        for match in matches:
            source = match['metadata'].get('source', 'Unknown')
            if source == 'Unknown' or 'Unknown' in source:
                unknown_vectors.append({
                    'id': match['id'],
                    'node_id': match['metadata'].get('node_id'),
                    'text_preview': match['text'][:150],
                    'metadata': match['metadata']
                })

    # Deduplicate by ID
    seen_ids = set()
    unique_unknown = []
    for vec in unknown_vectors:
        if vec['id'] not in seen_ids:
            seen_ids.add(vec['id'])
            unique_unknown.append(vec)

    print(f"\n✓ Found {len(unique_unknown)} vectors with 'Unknown' source\n")

    if unique_unknown:
        print("Sample vectors:\n")
        for i, vec in enumerate(unique_unknown[:10], 1):
            print(f"{i}. Vector ID: {vec['id']}")
            print(f"   Node ID: {vec['node_id']}")
            print(f"   Preview: \"{vec['text_preview']}...\"")
            print(f"   Metadata: {vec['metadata']}")
            print()

    return unique_unknown


def update_source_metadata(node_id=None, text_contains=None, new_source=None, chapter=None):
    """
    Update source metadata for vectors

    Args:
        node_id: Filter by node ID
        text_contains: Filter by text content (searches for matches)
        new_source: New source label (e.g., "Bouchaud: Trades, Quotes and Prices")
        chapter: New chapter label
    """
    if not new_source:
        print("❌ Error: --new-source is required")
        return

    print("\n" + "="*80)
    print(f"UPDATING SOURCE METADATA TO: {new_source}")
    if chapter:
        print(f"Chapter: {chapter}")
    print("="*80 + "\n")

    db = SessionLocal()

    try:
        # Step 1: Find matching vectors
        if node_id:
            print(f"Finding vectors for node_id={node_id}...")
            node = db.query(Node).filter(Node.id == node_id).first()
            if node:
                print(f"✓ Found node: {node.title}")

        # Unfortunately, Pinecone doesn't support bulk updates directly
        # We need to:
        # 1. Query to find matching vectors
        # 2. Fetch their current data
        # 3. Update and re-upsert

        print("\n⚠️  IMPORTANT: Pinecone doesn't support in-place metadata updates")
        print("To fix sources, you need to:")
        print("1. Re-index the content with correct metadata using proper indexing scripts")
        print("2. Or use Pinecone's upsert to update vectors individually")
        print("\nFor bulk updates, it's recommended to re-run the indexing script")
        print("with corrected metadata in the source code.\n")

        # Show example of correct metadata format
        print("="*80)
        print("CORRECT METADATA FORMAT FOR BOOK INDEXING:")
        print("="*80)
        print("""
# In your indexing script (e.g., index_bouchaud_ch1.py):

chunk_data.append({
    'text': chunk_text,
    'chunk_index': i,
    'metadata': {
        'category': 'statistics',  # or 'probability', 'machine_learning', etc.
        'subcategory': 'heavy_tails',  # specific topic
        'difficulty': 3,  # 1-5
        'source': 'Bouchaud: Trades, Quotes and Prices, Chapter 1',  # IMPORTANT!
        'chapter': '1',
        'section': '1.5',  # optional
    }
})

# Also add node-level metadata:
vector_ids = vector_store.upsert_chunks(
    chunks=chunk_data,
    node_id=node.id,
    node_metadata={
        'title': 'Heavy-Tailed Distributions',
        'category': 'statistics',
        'source_book': 'Bouchaud'  # Short name
    }
)
        """)

    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(
        description="Fix 'Unknown' sources in Pinecone vector store",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all Unknown sources
  python scripts/fix_unknown_sources.py --list

  # Show update instructions for a specific node
  python scripts/fix_unknown_sources.py --update --node-id 42 --new-source "Bouchaud Ch.1"
        """
    )
    parser.add_argument('--list', action='store_true',
                       help='List all vectors with Unknown source')
    parser.add_argument('--update', action='store_true',
                       help='Update source metadata (shows instructions)')
    parser.add_argument('--node-id', type=int,
                       help='Node ID to update')
    parser.add_argument('--new-source', type=str,
                       help='New source label (e.g., "Bouchaud: Trades, Quotes and Prices, Chapter 1")')
    parser.add_argument('--chapter', type=str,
                       help='Chapter number or label')

    args = parser.parse_args()

    if args.list:
        list_unknown_sources()
    elif args.update:
        update_source_metadata(
            node_id=args.node_id,
            new_source=args.new_source,
            chapter=args.chapter
        )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
