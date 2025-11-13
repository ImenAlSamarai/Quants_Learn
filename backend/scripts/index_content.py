"""
Content Indexing Pipeline

This script processes markdown/PDF content and indexes it into:
1. PostgreSQL (node metadata and structure)
2. Pinecone (text chunks with embeddings)

Usage:
    python scripts/index_content.py --content-dir ../content
"""

import os
import sys
import argparse
from pathlib import Path
import re
import markdown
from bs4 import BeautifulSoup

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.database import SessionLocal, Node, ContentChunk, init_db
from app.services.vector_store import vector_store
from app.config.settings import settings


class ContentIndexer:
    """Handles content processing and indexing"""

    def __init__(self):
        self.db = SessionLocal()
        self.chunk_size = settings.CHUNK_SIZE
        self.chunk_overlap = settings.CHUNK_OVERLAP

    def split_text(self, text: str) -> list:
        """Split text into overlapping chunks"""
        # Remove multiple newlines and extra spaces
        text = re.sub(r'\n\s*\n', '\n\n', text)

        # Split by paragraphs first
        paragraphs = text.split('\n\n')

        chunks = []
        current_chunk = ""

        for para in paragraphs:
            # If adding this paragraph exceeds chunk size, save current chunk
            if len(current_chunk) + len(para) > self.chunk_size and current_chunk:
                chunks.append(current_chunk.strip())

                # Start new chunk with overlap (last few words of previous chunk)
                words = current_chunk.split()
                overlap_words = words[-self.chunk_overlap:] if len(words) > self.chunk_overlap else words
                current_chunk = ' '.join(overlap_words) + '\n\n' + para
            else:
                current_chunk += '\n\n' + para if current_chunk else para

        # Add the last chunk
        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def process_markdown(self, file_path: str) -> dict:
        """Process a markdown file and extract metadata"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse frontmatter if exists (YAML format)
        metadata = {}
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                content = parts[2]

                # Parse simple YAML
                for line in frontmatter.strip().split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        metadata[key.strip()] = value.strip().strip('"\'')

        # Convert markdown to text
        html = markdown.markdown(content)
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text()

        # Extract title from first heading if not in metadata
        if 'title' not in metadata:
            first_heading = soup.find(['h1', 'h2'])
            if first_heading:
                metadata['title'] = first_heading.get_text()

        return {
            'metadata': metadata,
            'text': text,
            'raw_content': content
        }

    def index_node(
        self,
        title: str,
        category: str,
        subcategory: str,
        content_path: str,
        description: str = None,
        difficulty: int = 1,
        x_pos: float = 0,
        y_pos: float = 0,
        color: str = "#3b82f6",
        icon: str = "📚",
        parent_ids: list = None
    ):
        """Index a single node with its content"""

        # Create slug from title
        slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')

        # Check if node already exists
        existing_node = self.db.query(Node).filter(Node.slug == slug).first()

        if existing_node:
            print(f"Node '{title}' already exists. Updating...")
            node = existing_node
            # Update fields
            node.title = title
            node.category = category
            node.subcategory = subcategory
            node.description = description
            node.difficulty_level = difficulty
            node.x_position = x_pos
            node.y_position = y_pos
            node.color = color
            node.icon = icon
            node.content_path = content_path
        else:
            # Create new node
            node = Node(
                title=title,
                slug=slug,
                category=category,
                subcategory=subcategory,
                description=description,
                difficulty_level=difficulty,
                x_position=x_pos,
                y_position=y_pos,
                color=color,
                icon=icon,
                content_path=content_path
            )
            self.db.add(node)
            self.db.commit()
            self.db.refresh(node)
            print(f"Created node: {title} (ID: {node.id})")

        # Add parent relationships
        if parent_ids:
            parents = self.db.query(Node).filter(Node.id.in_(parent_ids)).all()
            node.parents = parents

        self.db.commit()
        self.db.refresh(node)

        # Process content if file exists
        if content_path and os.path.exists(content_path):
            print(f"Processing content from: {content_path}")

            # Parse markdown
            parsed = self.process_markdown(content_path)
            text = parsed['text']

            # Split into chunks
            chunks = self.split_text(text)
            print(f"Split into {len(chunks)} chunks")

            # Delete existing chunks for this node
            self.db.query(ContentChunk).filter(ContentChunk.node_id == node.id).delete()
            vector_store.delete_node_vectors(node.id)

            # Index chunks
            chunk_data = []
            for i, chunk_text in enumerate(chunks):
                chunk_data.append({
                    'text': chunk_text,
                    'chunk_index': i,
                    'metadata': {
                        'category': category,
                        'subcategory': subcategory,
                        'difficulty': difficulty
                    }
                })

            # Upload to Pinecone
            vector_ids = vector_store.upsert_chunks(
                chunks=chunk_data,
                node_id=node.id,
                node_metadata={
                    'title': title,
                    'category': category,
                    'subcategory': subcategory
                }
            )

            # Save chunk metadata to PostgreSQL
            for i, (chunk_text, vector_id) in enumerate(zip(chunks, vector_ids)):
                content_chunk = ContentChunk(
                    node_id=node.id,
                    chunk_text=chunk_text,
                    chunk_index=i,
                    vector_id=vector_id
                )
                self.db.add(content_chunk)

            self.db.commit()
            print(f"Indexed {len(chunks)} chunks for node '{title}'")

        return node.id

    def close(self):
        """Close database connection"""
        self.db.close()


def main():
    parser = argparse.ArgumentParser(description="Index learning content")
    parser.add_argument('--content-dir', default='../content', help='Content directory')
    parser.add_argument('--init-db', action='store_true', help='Initialize database')
    args = parser.parse_args()

    # Initialize database if requested
    if args.init_db:
        print("Initializing database...")
        init_db()

    indexer = ContentIndexer()

    print("Starting content indexing...")
    print("=" * 60)

    # Index Linear Algebra nodes
    # This is an example structure - you'll expand this based on your content
    try:
        # Root node: Linear Algebra
        la_root = indexer.index_node(
            title="Linear Algebra",
            category="linear_algebra",
            subcategory=None,
            content_path=os.path.join(args.content_dir, "linear_algebra/overview.md"),
            description="Mathematical study of vectors, matrices, and linear transformations",
            difficulty=2,
            x_pos=0,
            y_pos=0,
            color="#3b82f6",
            icon="🔷"
        )

        # Child nodes
        vectors_id = indexer.index_node(
            title="Vectors and Spaces",
            category="linear_algebra",
            subcategory="vectors",
            content_path=os.path.join(args.content_dir, "linear_algebra/vectors.md"),
            description="Vector operations, spaces, and properties",
            difficulty=1,
            x_pos=-2,
            y_pos=2,
            color="#60a5fa",
            icon="➡️",
            parent_ids=[la_root]
        )

        matrices_id = indexer.index_node(
            title="Matrix Operations",
            category="linear_algebra",
            subcategory="matrices",
            content_path=os.path.join(args.content_dir, "linear_algebra/matrices.md"),
            description="Matrix multiplication, inverses, and properties",
            difficulty=2,
            x_pos=0,
            y_pos=2,
            color="#60a5fa",
            icon="⊞",
            parent_ids=[la_root, vectors_id]
        )

        transforms_id = indexer.index_node(
            title="Linear Transformations",
            category="linear_algebra",
            subcategory="transformations",
            content_path=os.path.join(args.content_dir, "linear_algebra/transformations.md"),
            description="Linear maps and their matrix representations",
            difficulty=3,
            x_pos=2,
            y_pos=2,
            color="#60a5fa",
            icon="🔄",
            parent_ids=[la_root, matrices_id]
        )

        eigen_id = indexer.index_node(
            title="Eigenvalues and Eigenvectors",
            category="linear_algebra",
            subcategory="eigenvalues",
            content_path=os.path.join(args.content_dir, "linear_algebra/eigenvalues.md"),
            description="Spectral properties and diagonalization",
            difficulty=3,
            x_pos=-2,
            y_pos=4,
            color="#2563eb",
            icon="λ",
            parent_ids=[matrices_id, transforms_id]
        )

        # Advanced topics
        svd_id = indexer.index_node(
            title="SVD and Decompositions",
            category="linear_algebra",
            subcategory="decomposition",
            content_path=os.path.join(args.content_dir, "linear_algebra/svd.md"),
            description="Singular Value Decomposition, PCA, and matrix factorization",
            difficulty=4,
            x_pos=0,
            y_pos=4,
            color="#2563eb",
            icon="🔸",
            parent_ids=[eigen_id]
        )

        print("=" * 60)
        print("Content indexing completed successfully!")
        print(f"Total nodes indexed: 6")
        print("\nNext steps:")
        print("1. Start the backend server: python -m app.main")
        print("2. View indexed content at http://localhost:8000/api/nodes/mindmap")

    except Exception as e:
        print(f"Error during indexing: {e}")
        import traceback
        traceback.print_exc()

    finally:
        indexer.close()


if __name__ == "__main__":
    main()
