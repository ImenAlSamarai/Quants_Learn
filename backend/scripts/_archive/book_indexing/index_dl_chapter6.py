"""
Index Chapter 6 from Deep Learning: Foundations and Concepts - Deep Neural Networks

Creates topics:
1. Feedforward Neural Networks
2. Activation Functions
3. Output Units and Loss Functions
4. Universal Approximation

CRITICAL for quant interviews - Understanding neural network fundamentals.
"""

import os
import sys
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.database import SessionLocal, Node, ContentChunk, init_db
from app.services.vector_store import vector_store
from app.config.settings import settings
from dl_book_extractor import DeepLearningBookExtractor
import re


class Chapter6Indexer:
    """Indexer for Chapter 6: Deep Neural Networks"""

    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.db = SessionLocal()
        self.extractor = DeepLearningBookExtractor(pdf_path)
        self.chunk_size = settings.CHUNK_SIZE
        self.chunk_overlap = settings.CHUNK_OVERLAP

    def split_text(self, text: str) -> list:
        """
        Split text into overlapping chunks with hard token limit

        OpenAI embeddings have 8192 token limit, so we ensure chunks stay well below that.
        Using ~2000 characters per chunk (roughly 500 tokens) to be safe.
        """
        # Clean up text
        text = re.sub(r'\n\s*\n', '\n\n', text)

        # Maximum characters per chunk (roughly 500-700 tokens)
        max_chunk_chars = 2000

        chunks = []
        current_chunk = ""

        # Split by paragraphs first
        paragraphs = text.split('\n\n')

        for para in paragraphs:
            # If paragraph is extremely long (table, equation, etc), force split it
            if len(para) > max_chunk_chars * 2:
                # Save current chunk first
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = ""

                # Split long paragraph by character chunks
                for i in range(0, len(para), max_chunk_chars):
                    chunk = para[i:i + max_chunk_chars]
                    chunks.append(chunk.strip())
                continue

            # If paragraph is long but manageable, try splitting by sentences
            if len(para) > max_chunk_chars:
                sentences = re.split(r'(?<=[.!?])\s+', para)
                for sentence in sentences:
                    # If single sentence is too long, force split it
                    if len(sentence) > max_chunk_chars:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                            current_chunk = ""
                        # Split long sentence by characters
                        for i in range(0, len(sentence), max_chunk_chars):
                            chunks.append(sentence[i:i + max_chunk_chars].strip())
                        continue

                    # Normal sentence processing
                    if len(current_chunk) + len(sentence) > max_chunk_chars and current_chunk:
                        chunks.append(current_chunk.strip())
                        words = current_chunk.split()
                        overlap_words = words[-self.chunk_overlap:] if len(words) > self.chunk_overlap else words
                        current_chunk = ' '.join(overlap_words) + ' ' + sentence
                    else:
                        current_chunk += ' ' + sentence if current_chunk else sentence
            else:
                # Normal paragraph processing
                if len(current_chunk) + len(para) > max_chunk_chars and current_chunk:
                    chunks.append(current_chunk.strip())
                    words = current_chunk.split()
                    overlap_words = words[-self.chunk_overlap:] if len(words) > self.chunk_overlap else words
                    current_chunk = ' '.join(overlap_words) + '\n\n' + para
                else:
                    current_chunk += '\n\n' + para if current_chunk else para

        # Save any remaining chunk
        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def index_node(
        self,
        title: str,
        content: str,
        category: str = "machine_learning",
        subcategory: str = "deep_learning",
        description: str = None,
        difficulty: int = 4,
        x_pos: float = 0,
        y_pos: float = 0,
        color: str = "#8b5cf6",
        icon: str = "🧠",
        parent_ids: list = None
    ):
        """Index a topic with provided content"""

        slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')

        existing_node = self.db.query(Node).filter(Node.slug == slug).first()

        if existing_node:
            print(f"Updating existing node: {title}")
            node = existing_node
            node.title = title
            node.category = category
            node.subcategory = subcategory
            node.description = description
            node.difficulty_level = difficulty
            node.x_position = x_pos
            node.y_position = y_pos
            node.color = color
            node.icon = icon
        else:
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
                content_path=f"dl_chapter6_{slug}"
            )
            self.db.add(node)
            self.db.commit()
            self.db.refresh(node)
            print(f"Created node: {title} (ID: {node.id})")

        if parent_ids:
            parents = self.db.query(Node).filter(Node.id.in_(parent_ids)).all()
            node.parents = parents

        self.db.commit()
        self.db.refresh(node)

        # Process content
        if not content or not content.strip():
            print(f"Warning: No content for {title}")
            return node.id

        print(f"Content length: {len(content):,} characters")

        # Split into chunks
        chunks = self.split_text(content)
        print(f"Split into {len(chunks)} chunks")

        # Delete existing chunks
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
                    'difficulty': difficulty,
                    'source': 'Deep Learning: Foundations and Concepts, Chapter 6',
                }
            })

        # Upload to Pinecone
        vector_ids = vector_store.upsert_chunks(
            chunks=chunk_data,
            node_id=node.id,
            node_metadata={
                'title': title,
                'category': category,
                'subcategory': subcategory,
                'source_book': 'Deep Learning'
            }
        )

        # Save to PostgreSQL
        for i, (chunk_text, vector_id) in enumerate(zip(chunks, vector_ids)):
            content_chunk = ContentChunk(
                node_id=node.id,
                chunk_text=chunk_text,
                chunk_index=i,
                vector_id=vector_id
            )
            self.db.add(content_chunk)

        self.db.commit()
        print(f"✓ Indexed {len(chunks)} chunks for '{title}'")
        print()

        return node.id

    def close(self):
        self.db.close()
        self.extractor.close()


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Index Chapter 6 from DL book")
    parser.add_argument('--init-db', action='store_true', help='Initialize database')
    parser.add_argument('--pdf-path', default='../content/machine_learning/deep_learning_foundations_and_concepts.pdf')
    args = parser.parse_args()

    if args.init_db:
        print("Initializing database...")
        init_db()
        print()

    indexer = Chapter6Indexer(args.pdf_path)

    print("=" * 80)
    print("Chapter 6 Indexing: Deep Neural Networks")
    print("=" * 80)
    print()

    # Extract chapter
    chapter_data = indexer.extractor.extract_chapter(6)

    if not chapter_data:
        print("Failed to extract Chapter 6!")
        indexer.close()
        return

    chapter_text = chapter_data['text']
    print(f"Chapter 6 extracted: {len(chapter_text):,} characters")
    print(f"Pages: {chapter_data['start_page']}-{chapter_data['end_page']} ({chapter_data['page_count']} pages)")
    print()

    # Find parent node
    ml_root = indexer.db.query(Node).filter(Node.title == "Machine Learning").first()

    parent_ids = []
    if ml_root:
        parent_ids.append(ml_root.id)
        print(f"✓ Found parent: Machine Learning (ID: {ml_root.id})")
    print()

    try:
        # Split chapter into sections for topics
        lines = chapter_text.split('\n')
        total_lines = len(lines)

        # Topic 1: Feedforward Neural Networks (first ~25%)
        print("[1/4] Indexing: Feedforward Neural Networks")
        section_1 = '\n'.join(lines[:total_lines//4])

        indexer.index_node(
            title="Feedforward Neural Networks",
            content=section_1,
            description="Network architecture, hidden layers, weights and biases, forward propagation",
            difficulty=4,
            x_pos=-6,
            y_pos=20,
            icon="🔄",
            color="#8b5cf6",
            parent_ids=parent_ids
        )

        # Topic 2: Activation Functions (second quarter)
        print("[2/4] Indexing: Activation Functions")
        section_2 = '\n'.join(lines[total_lines//4:total_lines//2])

        indexer.index_node(
            title="Activation Functions",
            content=section_2,
            description="Sigmoid, tanh, ReLU, Leaky ReLU, Swish, nonlinearity in neural networks",
            difficulty=3,
            x_pos=-2,
            y_pos=20,
            icon="📈",
            color="#8b5cf6",
            parent_ids=parent_ids
        )

        # Topic 3: Output Units and Loss Functions (third quarter)
        print("[3/4] Indexing: Output Units and Loss Functions")
        section_3 = '\n'.join(lines[total_lines//2:3*total_lines//4])

        indexer.index_node(
            title="Output Units and Loss Functions",
            content=section_3,
            description="Regression output, classification output, softmax, cross-entropy, MSE loss",
            difficulty=4,
            x_pos=2,
            y_pos=20,
            icon="🎯",
            color="#8b5cf6",
            parent_ids=parent_ids
        )

        # Topic 4: Universal Approximation (last quarter)
        print("[4/4] Indexing: Universal Approximation")
        section_4 = '\n'.join(lines[3*total_lines//4:])

        indexer.index_node(
            title="Universal Approximation",
            content=section_4,
            description="Function approximation, representational capacity, depth vs width, expressiveness",
            difficulty=5,
            x_pos=6,
            y_pos=20,
            icon="∞",
            color="#8b5cf6",
            parent_ids=parent_ids
        )

        print("=" * 80)
        print("✓ Chapter 6 indexing completed successfully!")
        print()
        print("Topics added:")
        print("  Feedforward Neural Networks")
        print("  Activation Functions")
        print("  Output Units and Loss Functions")
        print("  Universal Approximation")
        print()
        print("Verify with:")
        print("  python scripts/check_indexed_content.py | grep -i 'neural\\|activation'")

    except Exception as e:
        print(f"Error during indexing: {e}")
        import traceback
        traceback.print_exc()

    finally:
        indexer.close()


if __name__ == "__main__":
    main()
