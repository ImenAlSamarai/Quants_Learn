#!/usr/bin/env python3
"""
Web Crawler and Indexer

Crawl a website starting from a URL and index all discovered pages.

Features:
- Respects robots.txt
- Configurable depth limit
- URL filtering (stay within domain/path)
- Rate limiting
- Deduplication

Usage:
    # Crawl entire documentation section
    python scripts/crawl_and_index.py \
        --url "https://scikit-learn.org/stable/modules/linear_model.html" \
        --depth 2 \
        --pattern "*/modules/linear_model*"

    # Crawl blog category
    python scripts/crawl_and_index.py \
        --url "https://towardsdatascience.com/tagged/machine-learning" \
        --depth 1 \
        --max-pages 20

    # Crawl with topic auto-detection
    python scripts/crawl_and_index.py \
        --url "https://docs.python.org/3/tutorial/" \
        --depth 2 \
        --topic "Python Programming"
"""

import sys
import os
import argparse
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser
import time
import fnmatch
from collections import deque

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from index_web_resource import WebResourceIndexer
import requests
from bs4 import BeautifulSoup


class WebCrawler:
    """Crawl website and index pages"""

    def __init__(
        self,
        start_url: str,
        max_depth: int = 2,
        max_pages: int = 100,
        pattern: str = None,
        same_domain: bool = True,
        delay: int = 2
    ):
        self.start_url = start_url
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.pattern = pattern
        self.same_domain = same_domain
        self.delay = delay

        self.visited = set()
        self.to_visit = deque([(start_url, 0)])  # (url, depth)
        self.indexed_count = 0

        # Setup robot parser
        parsed = urlparse(start_url)
        self.base_domain = f"{parsed.scheme}://{parsed.netloc}"
        self.start_path = parsed.path

        self.robot_parser = RobotFileParser()
        robots_url = f"{self.base_domain}/robots.txt"
        try:
            self.robot_parser.set_url(robots_url)
            self.robot_parser.read()
            print(f"✅ Loaded robots.txt from {robots_url}")
        except:
            print(f"⚠️  No robots.txt found at {robots_url}, proceeding carefully")

        self.indexer = WebResourceIndexer()

    def extract_topic_from_title(self, title: str, url: str) -> str:
        """
        Extract clean topic name from page title

        Removes common prefixes like:
        - "Documentation - Linear Regression" → "Linear Regression"
        - "Scikit-Learn: Ridge Regression" → "Ridge Regression"
        - "PyTorch Docs: Neural Networks" → "Neural Networks"
        """
        import re

        # Common prefixes to remove
        prefixes_to_remove = [
            r'^Documentation[\s\-:]+',
            r'^Docs[\s\-:]+',
            r'^Tutorial[\s\-:]+',
            r'^Guide[\s\-:]+',
            r'^\d+\.\d+\.\d+[\s\-:]+',  # Version numbers like "1.2.3 - "
            r'^[A-Za-z\-]+\s*(?:Documentation|Docs|Tutorial)[\s\-:]+',  # "PyTorch Documentation - "
        ]

        clean_title = title
        for prefix_pattern in prefixes_to_remove:
            clean_title = re.sub(prefix_pattern, '', clean_title, flags=re.IGNORECASE)

        # Also try to extract from URL if title is too generic
        if len(clean_title.split()) <= 2 or clean_title.lower() in ['documentation', 'docs', 'home', 'index']:
            # Extract from URL path
            # e.g., ".../linear_model/ridge.html" → "Ridge"
            path_parts = urlparse(url).path.split('/')
            if len(path_parts) > 1:
                # Get last meaningful part
                last_part = path_parts[-1].replace('.html', '').replace('.php', '').replace('_', ' ').title()
                if last_part and last_part.lower() not in ['index', 'home', 'readme']:
                    clean_title = last_part

        return clean_title.strip()

    def is_allowed(self, url: str) -> bool:
        """Check if URL is allowed by robots.txt"""
        try:
            return self.robot_parser.can_fetch("*", url)
        except:
            return True  # If robots.txt check fails, allow

    def should_crawl(self, url: str, depth: int) -> bool:
        """Determine if URL should be crawled"""

        # Already visited
        if url in self.visited:
            return False

        # Max depth exceeded
        if depth > self.max_depth:
            return False

        # Max pages reached
        if self.indexed_count >= self.max_pages:
            return False

        # Check robots.txt
        if not self.is_allowed(url):
            print(f"  ⛔ Blocked by robots.txt: {url}")
            return False

        parsed = urlparse(url)

        # Same domain only
        if self.same_domain:
            url_domain = f"{parsed.scheme}://{parsed.netloc}"
            if url_domain != self.base_domain:
                return False

        # URL pattern matching
        if self.pattern:
            if not fnmatch.fnmatch(url, self.pattern):
                return False

        # Skip common non-content URLs
        skip_patterns = [
            '*/login', '*/signup', '*/register',
            '*/cart', '*/checkout',
            '*.pdf', '*.zip', '*.tar.gz',
            '*/search?', '*/api/*',
            '#*'  # Skip anchors
        ]

        for skip_pattern in skip_patterns:
            if fnmatch.fnmatch(url, skip_pattern):
                return False

        return True

    def extract_links(self, url: str, html: str) -> list:
        """Extract links from HTML content"""
        soup = BeautifulSoup(html, 'html.parser')
        links = []

        for link in soup.find_all('a', href=True):
            href = link['href']

            # Convert relative URLs to absolute
            absolute_url = urljoin(url, href)

            # Remove fragments
            parsed = urlparse(absolute_url)
            clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            if parsed.query:
                clean_url += f"?{parsed.query}"

            links.append(clean_url)

        return list(set(links))  # Deduplicate

    def crawl_and_index(self, topic: str = None, source: str = None, category: str = "web_resource"):
        """
        Crawl website and index all pages

        Args:
            topic: Topic name (auto-detect from page title if None)
            source: Source name (auto-detect from domain if None)
            category: Category for organization
        """
        print(f"\n{'='*80}")
        print(f"WEB CRAWLER STARTING")
        print(f"{'='*80}")
        print(f"Start URL: {self.start_url}")
        print(f"Max Depth: {self.max_depth}")
        print(f"Max Pages: {self.max_pages}")
        print(f"Same Domain: {self.same_domain}")
        print(f"Pattern: {self.pattern or 'None (all URLs)'}")
        print(f"{'='*80}\n")

        while self.to_visit and self.indexed_count < self.max_pages:
            url, depth = self.to_visit.popleft()

            # Skip if shouldn't crawl
            if not self.should_crawl(url, depth):
                continue

            # Mark as visited
            self.visited.add(url)

            print(f"\n[{self.indexed_count + 1}/{self.max_pages}] Depth {depth}: {url}")

            try:
                # Fetch page
                headers = {'User-Agent': 'Mozilla/5.0 (Educational Crawler)'}
                response = requests.get(url, headers=headers, timeout=30)
                response.raise_for_status()

                # Extract links for crawling (before indexing)
                if depth < self.max_depth:
                    links = self.extract_links(url, response.content)
                    print(f"  🔗 Found {len(links)} links")

                    # Add to queue
                    for link in links:
                        if link not in self.visited:
                            self.to_visit.append((link, depth + 1))

                # Index this page
                page_data = self.indexer.fetch_webpage(url)

                # Extract clean topic from page title and URL
                clean_topic = self.extract_topic_from_title(page_data['title'], url)

                # If global topic provided, use it as category/prefix
                if topic:
                    page_topic = f"{topic}: {clean_topic}"
                else:
                    page_topic = clean_topic

                page_source = source or page_data['domain']

                print(f"  📌 Topic: {page_topic}")

                # Index the page
                chunks = self.indexer.split_text(page_data['text'])
                print(f"  📝 {len(chunks)} chunks")

                metadata_list = []
                for i, chunk in enumerate(chunks):
                    metadata = {
                        'text': chunk,
                        'source': page_source,
                        'url': url,
                        'topic': page_topic,
                        'category': category,
                        'subcategory': 'crawled_content',
                        'chunk_index': i,
                        'total_chunks': len(chunks),
                        'title': page_data['title'],
                        'content_type': 'web_page',
                        'crawl_depth': depth
                    }
                    metadata_list.append(metadata)

                # Upsert to Pinecone
                from app.services.vector_store import vector_store
                vector_store.upsert_chunks(
                    chunks=chunks,
                    metadata_list=metadata_list,
                    namespace=category
                )

                print(f"  ✅ Indexed: {page_topic}")
                self.indexed_count += 1

                # Rate limiting
                time.sleep(self.delay)

            except Exception as e:
                print(f"  ❌ Error: {e}")
                continue

        # Summary
        print(f"\n{'='*80}")
        print(f"CRAWL COMPLETE")
        print(f"{'='*80}")
        print(f"Pages indexed: {self.indexed_count}")
        print(f"Pages visited: {len(self.visited)}")
        print(f"Pages remaining: {len(self.to_visit)}")
        print(f"{'='*80}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Crawl and index website pages",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Crawl documentation section (2 levels deep)
    python scripts/crawl_and_index.py \\
        --url "https://scikit-learn.org/stable/modules/linear_model.html" \\
        --depth 2 \\
        --pattern "*/modules/linear_model*"

    # Crawl blog category (max 20 pages)
    python scripts/crawl_and_index.py \\
        --url "https://towardsdatascience.com/tagged/statistics" \\
        --depth 1 \\
        --max-pages 20 \\
        --topic "Statistics"

    # Crawl tutorial series
    python scripts/crawl_and_index.py \\
        --url "https://docs.python.org/3/tutorial/" \\
        --depth 2 \\
        --topic "Python Tutorial" \\
        --source "Python Docs"

    # Crawl entire documentation site (careful!)
    python scripts/crawl_and_index.py \\
        --url "https://pytorch.org/docs/stable/index.html" \\
        --depth 3 \\
        --max-pages 50 \\
        --delay 3
        """
    )

    parser.add_argument('--url', required=True, help='Starting URL')
    parser.add_argument('--depth', type=int, default=2, help='Max crawl depth (default: 2)')
    parser.add_argument('--max-pages', type=int, default=100, help='Max pages to index (default: 100)')
    parser.add_argument('--pattern', help='URL pattern to match (e.g., "*/docs/stable/*")')
    parser.add_argument(
        '--topic',
        help='Optional category prefix. Each page auto-detects its own topic from title. '
             'If provided, format will be "Category: Page Topic" (e.g., "ML Docs: Linear Regression")'
    )
    parser.add_argument('--source', help='Source name (auto-detect from domain if not provided)')
    parser.add_argument('--category', default='web_resource', help='Category (default: web_resource)')
    parser.add_argument('--delay', type=int, default=2, help='Delay between requests in seconds (default: 2)')
    parser.add_argument('--allow-external', action='store_true', help='Allow crawling external domains')

    args = parser.parse_args()

    # Create crawler
    crawler = WebCrawler(
        start_url=args.url,
        max_depth=args.depth,
        max_pages=args.max_pages,
        pattern=args.pattern,
        same_domain=not args.allow_external,
        delay=args.delay
    )

    # Crawl and index
    crawler.crawl_and_index(
        topic=args.topic,
        source=args.source,
        category=args.category
    )

    print("✅ Crawling and indexing complete!")
    print("\n💡 Indexed pages are now searchable in your RAG system.")


if __name__ == "__main__":
    main()
