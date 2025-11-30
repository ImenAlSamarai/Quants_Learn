#!/usr/bin/env python3
"""
Enhanced Web URL Indexer - Multi-Topic Support

Index web pages with multiple topics for better discoverability.

Usage:
    # Single URL, multiple topics
    python scripts/index_url_multitopic.py \
        --url "https://example.com/guide" \
        --topics "Linear Regression,Hypothesis Testing,ANOVA"

    # From file with multi-topic format
    python scripts/index_url_multitopic.py --file urls_multitopic.txt

File format:
    URL | Topic1, Topic2, Topic3 | Source Name

Example:
    https://example.com/stats | Linear Regression, Hypothesis Testing, ANOVA | Example Site
"""

import sys
import os
import argparse
from pathlib import Path
import time

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from index_web_resource import WebResourceIndexer


def parse_multitopic_file(file_path: str) -> list:
    """
    Parse URLs file with multi-topic support

    Format per line:
        URL | Topic1, Topic2, Topic3 | Source Name (optional)

    Returns:
        List of dicts: [{'url': ..., 'topics': [...], 'source': ...}, ...]
    """
    url_entries = []

    with open(file_path, 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()

            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue

            # Parse line
            parts = [p.strip() for p in line.split('|')]

            if len(parts) < 2:
                print(f"⚠️  Line {line_num}: Invalid format (need at least URL | Topics)")
                continue

            url = parts[0]
            topics_str = parts[1]
            source = parts[2] if len(parts) > 2 else None

            # Parse multiple topics (comma-separated)
            topics = [t.strip() for t in topics_str.split(',')]

            url_entries.append({
                'url': url,
                'topics': topics,
                'source': source
            })

    return url_entries


def index_url_multitopic(url: str, topics: list, source: str = None, category: str = "web_resource"):
    """
    Index a single URL with multiple topic tags

    Args:
        url: URL to index
        topics: List of topic names
        source: Source name (optional)
        category: Category for organization
    """
    indexer = WebResourceIndexer()

    print(f"\n{'='*80}")
    print(f"Indexing URL with {len(topics)} topics")
    print(f"{'='*80}")
    print(f"URL: {url}")
    print(f"Topics: {', '.join(topics)}")
    print(f"Source: {source or 'Auto-detect'}")
    print(f"{'='*80}\n")

    try:
        # Fetch webpage content once
        page_data = indexer.fetch_webpage(url)

        if source is None:
            source = page_data['domain']

        # Split into chunks once
        chunks = indexer.split_text(page_data['text'])
        print(f"📝 Split into {len(chunks)} chunks")

        # Index with ALL topics in metadata
        print(f"🚀 Indexing to Pinecone with {len(topics)} topic tags...")

        metadata_list = []
        for i, chunk in enumerate(chunks):
            # Create metadata with ALL topics
            metadata = {
                'text': chunk,
                'source': source,
                'url': url,
                'topics': topics,  # ALL topics in a list
                'primary_topic': topics[0],  # First topic as primary
                'category': category,
                'subcategory': 'online_article',
                'chunk_index': i,
                'total_chunks': len(chunks),
                'title': page_data['title'],
                'content_type': 'web_article'
            }
            metadata_list.append(metadata)

        # Batch upsert to Pinecone
        from app.services.vector_store import vector_store
        vector_store.upsert_web_chunks(
            chunks=chunks,
            metadata_list=metadata_list,
            namespace=category
        )

        print(f"✅ Indexed {len(chunks)} chunks from {url}")
        print(f"   Topics covered: {', '.join(topics)}")
        print(f"   Each chunk tagged with ALL topics for better matching")

        return True

    except Exception as e:
        print(f"❌ Failed to index {url}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Index web URLs with multiple topic support",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Single URL with multiple topics
    python scripts/index_url_multitopic.py \\
        --url "https://example.com/guide" \\
        --topics "Linear Regression,Hypothesis Testing,ANOVA"

    # From file
    python scripts/index_url_multitopic.py --file urls_multitopic.txt

    # File format:
    # URL | Topic1, Topic2, Topic3 | Source
    # https://example.com/stats | Linear Regression, Hypothesis Testing | Example Site
        """
    )

    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--url', help='Single URL to index')
    input_group.add_argument('--file', help='Path to URLs file')

    # Additional options
    parser.add_argument('--topics', help='Comma-separated topics (required for --url)')
    parser.add_argument('--source', help='Source name (optional)')
    parser.add_argument('--category', default='web_resource', help='Category (default: web_resource)')

    args = parser.parse_args()

    # Process input
    if args.url:
        # Single URL mode
        if not args.topics:
            print("❌ Error: --topics is required when using --url")
            print("\nExample:")
            print("  python scripts/index_url_multitopic.py \\")
            print("      --url 'https://example.com' \\")
            print("      --topics 'Topic 1,Topic 2,Topic 3'")
            sys.exit(1)

        topics = [t.strip() for t in args.topics.split(',')]

        success = index_url_multitopic(
            url=args.url,
            topics=topics,
            source=args.source,
            category=args.category
        )

        sys.exit(0 if success else 1)

    elif args.file:
        # File mode
        if not os.path.exists(args.file):
            print(f"❌ Error: File not found: {args.file}")
            sys.exit(1)

        url_entries = parse_multitopic_file(args.file)

        if not url_entries:
            print(f"❌ Error: No valid URLs found in {args.file}")
            print("\nExpected format per line:")
            print("  URL | Topic1, Topic2, Topic3 | Source Name (optional)")
            print("\nExample:")
            print("  https://example.com | Linear Regression, ANOVA | Example Site")
            sys.exit(1)

        # Process each URL
        total = len(url_entries)
        success_count = 0

        print(f"\n{'='*80}")
        print(f"BATCH MULTI-TOPIC INDEXING - {total} URLs")
        print(f"{'='*80}\n")

        for i, entry in enumerate(url_entries, 1):
            print(f"\n[{i}/{total}] Processing URL...")

            success = index_url_multitopic(
                url=entry['url'],
                topics=entry['topics'],
                source=entry.get('source'),
                category=args.category
            )

            if success:
                success_count += 1

            # Rate limiting
            if i < total:
                print("  ⏱️  Waiting 2 seconds...")
                time.sleep(2)

        # Summary
        print(f"\n{'='*80}")
        print(f"BATCH INDEXING COMPLETE")
        print(f"{'='*80}")
        print(f"✅ Success: {success_count}/{total}")
        print(f"❌ Failed: {total - success_count}/{total}")
        print()


if __name__ == "__main__":
    main()
