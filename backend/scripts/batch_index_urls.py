#!/usr/bin/env python3
"""
Batch Web URL Indexer

Index multiple web URLs from a file or command line.

Usage:
    # From file
    python scripts/batch_index_urls.py --file urls.txt

    # Single URL (quick)
    python scripts/batch_index_urls.py \
        --url "https://example.com/article" \
        --topic "Topic Name"

    # Multiple URLs directly
    python scripts/batch_index_urls.py \
        --urls "url1,Topic1" "url2,Topic2"
"""

import sys
import os
import argparse
from pathlib import Path
import time

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from index_web_resource import WebResourceIndexer


def parse_urls_file(file_path: str) -> list:
    """
    Parse URLs from text file

    Format per line:
        URL | Topic Name | Source Name (optional)

    Returns:
        List of dicts: [{'url': ..., 'topic': ..., 'source': ...}, ...]
    """
    urls = []

    with open(file_path, 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()

            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue

            # Parse line
            parts = [p.strip() for p in line.split('|')]

            if len(parts) < 2:
                print(f"⚠️  Line {line_num}: Invalid format (need at least URL | Topic)")
                continue

            url = parts[0]
            topic = parts[1]
            source = parts[2] if len(parts) > 2 else None

            urls.append({
                'url': url,
                'topic': topic,
                'source': source
            })

    return urls


def index_urls(urls_data: list, category: str = "web_resource"):
    """
    Index multiple URLs

    Args:
        urls_data: List of dicts with url, topic, source
        category: Category for all URLs
    """
    indexer = WebResourceIndexer()

    total = len(urls_data)
    print(f"\n{'='*80}")
    print(f"BATCH WEB INDEXING - {total} URLs")
    print(f"{'='*80}\n")

    success_count = 0
    failed_urls = []

    for i, data in enumerate(urls_data, 1):
        url = data['url']
        topic = data['topic']
        source = data.get('source')

        print(f"\n[{i}/{total}] Processing: {topic}")
        print(f"  URL: {url}")

        try:
            indexer.index_web_resource(
                url=url,
                topic=topic,
                source_name=source,
                category=category
            )
            success_count += 1

            # Rate limiting - be nice to servers
            if i < total:
                print("  ⏱️  Waiting 2 seconds before next request...")
                time.sleep(2)

        except Exception as e:
            print(f"  ❌ Failed: {e}")
            failed_urls.append({'url': url, 'topic': topic, 'error': str(e)})
            continue

    # Summary
    print(f"\n{'='*80}")
    print(f"BATCH INDEXING COMPLETE")
    print(f"{'='*80}")
    print(f"✅ Success: {success_count}/{total}")
    print(f"❌ Failed: {len(failed_urls)}/{total}")

    if failed_urls:
        print("\n⚠️  Failed URLs:")
        for item in failed_urls:
            print(f"  - {item['topic']}: {item['url']}")
            print(f"    Error: {item['error']}")

    print()


def main():
    parser = argparse.ArgumentParser(
        description="Batch index web URLs for RAG",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Index from file
    python scripts/batch_index_urls.py --file urls.txt

    # Single URL (quick way)
    python scripts/batch_index_urls.py \\
        --url "https://towardsdatascience.com/article" \\
        --topic "Machine Learning Basics"

    # Multiple URLs inline
    python scripts/batch_index_urls.py \\
        --urls "https://url1.com,Topic 1" "https://url2.com,Topic 2"

    # With custom category
    python scripts/batch_index_urls.py --file urls.txt --category trading
        """
    )

    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        '--file',
        help='Path to text file with URLs (format: URL | Topic | Source)'
    )
    input_group.add_argument(
        '--url',
        help='Single URL to index (must also provide --topic)'
    )
    input_group.add_argument(
        '--urls',
        nargs='+',
        help='Multiple URLs in format "url,topic" or "url,topic,source"'
    )

    # Additional options
    parser.add_argument(
        '--topic',
        help='Topic name (required if using --url)'
    )
    parser.add_argument(
        '--source',
        help='Source name (optional, for --url mode)'
    )
    parser.add_argument(
        '--category',
        default='web_resource',
        help='Category for organization (default: web_resource)'
    )

    args = parser.parse_args()

    # Prepare URLs list
    urls_data = []

    if args.file:
        # Load from file
        if not os.path.exists(args.file):
            print(f"❌ Error: File not found: {args.file}")
            sys.exit(1)

        urls_data = parse_urls_file(args.file)

        if not urls_data:
            print(f"❌ Error: No valid URLs found in {args.file}")
            print("\nExpected format per line:")
            print("  URL | Topic Name | Source Name (optional)")
            print("\nExample:")
            print("  https://example.com/article | Machine Learning | Example Blog")
            sys.exit(1)

    elif args.url:
        # Single URL mode
        if not args.topic:
            print("❌ Error: --topic is required when using --url")
            sys.exit(1)

        urls_data = [{
            'url': args.url,
            'topic': args.topic,
            'source': args.source
        }]

    elif args.urls:
        # Multiple URLs inline
        for url_spec in args.urls:
            parts = [p.strip() for p in url_spec.split(',')]

            if len(parts) < 2:
                print(f"⚠️  Skipping invalid URL spec: {url_spec}")
                print("    Expected format: 'url,topic' or 'url,topic,source'")
                continue

            urls_data.append({
                'url': parts[0],
                'topic': parts[1],
                'source': parts[2] if len(parts) > 2 else None
            })

    # Index URLs
    index_urls(urls_data, category=args.category)


if __name__ == "__main__":
    main()
