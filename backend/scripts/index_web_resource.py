"""
Web Resource Indexing Script

Fetches content from web pages and indexes them into Pinecone for RAG.
Useful for including online tutorials, documentation, and articles.

Usage:
    python scripts/index_web_resource.py --url "https://example.com/article" --topic "Statistical Modeling"

    # With specific metadata
    python scripts/index_web_resource.py \
        --url "https://stats.stackexchange.com/..." \
        --topic "Bayesian Statistics" \
        --source-name "Cross Validated" \
        --category "statistics"
"""

import os
import sys
import argparse
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.database import SessionLocal, Node, ContentChunk, init_db
from app.services.vector_store import vector_store
from app.config.settings import settings


class WebResourceIndexer:
    """Handles web content fetching and indexing"""

    def __init__(self):
        self.db = SessionLocal()
        self.chunk_size = settings.CHUNK_SIZE
        self.chunk_overlap = settings.CHUNK_OVERLAP

    def fetch_webpage(self, url: str) -> dict:
        """
        Fetch and extract clean text from a webpage

        Returns:
            dict with 'title', 'text', 'url', 'domain'
        """
        try:
            print(f"📡 Fetching {url}...")

            headers = {
                'User-Agent': 'Mozilla/5.0 (Educational RAG System)'
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()

            # Extract title
            title = soup.find('title')
            title_text = title.get_text().strip() if title else urlparse(url).path

            # Extract main content (try common content containers)
            main_content = (
                soup.find('main') or
                soup.find('article') or
                soup.find('div', {'class': re.compile(r'content|article|post', re.I)}) or
                soup.find('body')
            )

            # Get clean text
            text = main_content.get_text(separator='\n', strip=True) if main_content else ""

            # Clean up extra whitespace
            text = re.sub(r'\n\s*\n', '\n\n', text)
            text = re.sub(r' +', ' ', text)

            domain = urlparse(url).netloc

            print(f"✅ Fetched: {title_text} ({len(text)} chars)")

            return {
                'title': title_text,
                'text': text,
                'url': url,
                'domain': domain
            }

        except Exception as e:
            print(f"❌ Error fetching {url}: {e}")
            raise

    def split_text(self, text: str) -> list:
        """Split text into overlapping chunks"""
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""

        for para in paragraphs:
            if len(current_chunk) + len(para) > self.chunk_size and current_chunk:
                chunks.append(current_chunk.strip())

                # Overlap with previous chunk
                words = current_chunk.split()
                overlap_words = words[-self.chunk_overlap:] if len(words) > self.chunk_overlap else words
                current_chunk = ' '.join(overlap_words) + '\n\n' + para
            else:
                current_chunk += '\n\n' + para if current_chunk else para

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def index_web_resource(
        self,
        url: str,
        topic: str,
        source_name: str = None,
        category: str = "web_resource",
        subcategory: str = "online_article"
    ):
        """
        Fetch webpage and index it into Pinecone

        Args:
            url: URL of the webpage to index
            topic: Topic/title for categorization (e.g., "Bayesian Inference")
            source_name: Display name for the source (e.g., "Towards Data Science")
            category: Category for organization
            subcategory: Subcategory for organization
        """

        # Fetch webpage content
        page_data = self.fetch_webpage(url)

        if source_name is None:
            source_name = page_data['domain']

        # Split into chunks
        chunks = self.split_text(page_data['text'])
        print(f"📝 Split into {len(chunks)} chunks")

        # Index into Pinecone
        print(f"🚀 Indexing to Pinecone...")

        metadata_list = []
        for i, chunk in enumerate(chunks):
            metadata = {
                'text': chunk,
                'source': source_name,
                'url': url,
                'topic': topic,
                'category': category,
                'subcategory': subcategory,
                'chunk_index': i,
                'total_chunks': len(chunks),
                'title': page_data['title'],
                'content_type': 'web_article'
            }
            metadata_list.append(metadata)

        # Batch upsert to Pinecone
        vector_store.upsert_web_chunks(
            chunks=chunks,
            metadata_list=metadata_list,
            namespace=category
        )

        print(f"✅ Indexed {len(chunks)} chunks from {url}")
        print(f"   Topic: {topic}")
        print(f"   Source: {source_name}")
        print(f"   Category: {category}/{subcategory}")


def main():
    parser = argparse.ArgumentParser(description="Index web resources for RAG")
    parser.add_argument('--url', required=True, help='URL of the webpage to index')
    parser.add_argument('--topic', required=True, help='Topic name (e.g., "Maximum Likelihood Estimation")')
    parser.add_argument('--source-name', help='Source display name (e.g., "Towards Data Science")')
    parser.add_argument('--category', default='web_resource', help='Category for organization')
    parser.add_argument('--subcategory', default='online_article', help='Subcategory')

    args = parser.parse_args()

    print("=" * 60)
    print("WEB RESOURCE INDEXER")
    print("=" * 60)

    # Initialize database
    init_db()

    # Create indexer
    indexer = WebResourceIndexer()

    # Index the web resource
    indexer.index_web_resource(
        url=args.url,
        topic=args.topic,
        source_name=args.source_name,
        category=args.category,
        subcategory=args.subcategory
    )

    print("\n✅ Done! Web resource indexed successfully.")
    print("\n💡 You can now use this content in your RAG queries.")


if __name__ == "__main__":
    main()
