"""
Index Chapters 7-8 from Deep Learning: Foundations and Concepts - Training Neural Networks

Creates topics:
1. Gradient Descent and Optimization
2. Backpropagation Algorithm
3. Advanced Optimizers (Adam, RMSprop, Momentum)
4. Batch Normalization and Layer Normalization

CRITICAL for quant interviews - Understanding how neural networks learn.
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


class Chapters7_8_Indexer:
    """Indexer for Chapters 7-8: Gradient Descent and Backpropagation"""

    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.db = SessionLocal()
        self.extractor = DeepLearningBookExtractor(pdf_path)
        self.chunk_size = settings.CHUNK_SIZE
        self.chunk_overlap = settings.CHUNK_OVERLAP

    def split_text(self, text: str) -> list:
        """Split text into overlapping chunks with hard token limit"""
        text = re.sub(r'\n\s*\n', '\n\n', text)
        max_chunk_chars = 2000

        chunks = []
        current_chunk = ""
        paragraphs = text.split('\n\n')

        for para in paragraphs:
            if len(para) > max_chunk_chars * 2:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = ""
                for i in range(0, len(para), max_chunk_chars):
                    chunk = para[i:i + max_chunk_chars]
                    chunks.append(chunk.strip())
                continue

            if len(para) > max_chunk_chars:
                sentences = re.split(r'(?<=[.!?])\s+', para)
                for sentence in sentences:
                    if len(sentence) > max_chunk_chars:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                            current_chunk = ""
                        for i in range(0, len(sentence), max_chunk_chars):
                            chunks.append(sentence[i:i + max_chunk_chars].strip())
                        continue

                    if len(current_chunk) + len(sentence) > max_chunk_chars and current_chunk:
                        chunks.append(current_chunk.strip())
                        words = current_chunk.split()
                        overlap_words = words[-self.chunk_overlap:] if len(words) > self.chunk_overlap else words
                        current_chunk = ' '.join(overlap_words) + ' ' + sentence
                    else:
                        current_chunk += ' ' + sentence if current_chunk else sentence
            else:
                if len(current_chunk) + len(para) > max_chunk_chars and current_chunk:
                    chunks.append(current_chunk.strip())
                    words = current_chunk.split()
                    overlap_words = words[-self.chunk_overlap:] if len(words) > self.chunk_overlap else words
                    current_chunk = ' '.join(overlap_words) + '\n\n' + para
                else:
                    current_chunk += '\n\n' + para if current_chunk else para

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
                content_path=f"dl_chapters7_8_{slug}"
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

        if not content or not content.strip():
            print(f"Warning: No content for {title}")
            return node.id

        print(f"Content length: {len(content):,} characters")

        chunks = self.split_text(content)
        print(f"Split into {len(chunks)} chunks")

        self.db.query(ContentChunk).filter(ContentChunk.node_id == node.id).delete()
        vector_store.delete_node_vectors(node.id)

        chunk_data = []
        for i, chunk_text in enumerate(chunks):
            chunk_data.append({
                'text': chunk_text,
                'chunk_index': i,
                'metadata': {
                    'category': category,
                    'subcategory': subcategory,
                    'difficulty': difficulty,
                    'source': 'Deep Learning: Foundations and Concepts, Chapters 7-8',
                }
            })

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

    parser = argparse.ArgumentParser(description="Index Chapters 7-8 from DL book")
    parser.add_argument('--init-db', action='store_true', help='Initialize database')
    parser.add_argument('--pdf-path', default='../content/machine_learning/deep_learning_foundations_and_concepts.pdf')
    args = parser.parse_args()

    if args.init_db:
        print("Initializing database...")
        init_db()
        print()

    indexer = Chapters7_8_Indexer(args.pdf_path)

    print("=" * 80)
    print("Chapters 7-8 Indexing: Training Neural Networks")
    print("=" * 80)
    print()

    # Extract both chapters
    chapter7_data = indexer.extractor.extract_chapter(7)
    chapter8_data = indexer.extractor.extract_chapter(8)

    if not chapter7_data or not chapter8_data:
        print("Failed to extract chapters!")
        indexer.close()
        return

    chapter7_text = chapter7_data['text']
    chapter8_text = chapter8_data['text']

    print(f"Chapter 7 extracted: {len(chapter7_text):,} characters")
    print(f"Chapter 8 extracted: {len(chapter8_text):,} characters")
    print()

    ml_root = indexer.db.query(Node).filter(Node.title == "Machine Learning").first()

    parent_ids = []
    if ml_root:
        parent_ids.append(ml_root.id)
        print(f"✓ Found parent: Machine Learning (ID: {ml_root.id})")
    print()

    try:
        # Topic 1: Gradient Descent (first half of Chapter 7)
        print("[1/4] Indexing: Gradient Descent and Optimization")
        lines7 = chapter7_text.split('\n')
        gd_content = '\n'.join(lines7[:len(lines7)//2])

        indexer.index_node(
            title="Gradient Descent and Optimization",
            content=gd_content,
            description="Gradient descent, learning rate, stochastic gradient descent (SGD), mini-batches, convergence",
            difficulty=4,
            x_pos=-6,
            y_pos=22,
            icon="📉",
            color="#8b5cf6",
            parent_ids=parent_ids
        )

        # Topic 2: Backpropagation (Chapter 8 content)
        print("[2/4] Indexing: Backpropagation Algorithm")
        lines8 = chapter8_text.split('\n')
        backprop_content = '\n'.join(lines8[:len(lines8)//2])

        indexer.index_node(
            title="Backpropagation Algorithm",
            content=backprop_content,
            description="Chain rule, backward pass, gradient computation, computational graphs, automatic differentiation",
            difficulty=5,
            x_pos=-2,
            y_pos=22,
            icon="⬅️",
            color="#8b5cf6",
            parent_ids=parent_ids
        )

        # Topic 3: Advanced Optimizers (second half of Chapter 7)
        print("[3/4] Indexing: Advanced Optimizers")
        advanced_opt_content = '\n'.join(lines7[len(lines7)//2:])

        indexer.index_node(
            title="Advanced Optimizers (Adam, RMSprop, Momentum)",
            content=advanced_opt_content,
            description="Momentum, Nesterov, AdaGrad, RMSprop, Adam optimizer, adaptive learning rates",
            difficulty=4,
            x_pos=2,
            y_pos=22,
            icon="🚀",
            color="#8b5cf6",
            parent_ids=parent_ids
        )

        # Topic 4: Batch/Layer Normalization (second half of Chapter 8 or end of 7)
        print("[4/4] Indexing: Batch Normalization and Layer Normalization")
        norm_content = '\n'.join(lines8[len(lines8)//2:])

        indexer.index_node(
            title="Batch Normalization and Layer Normalization",
            content=norm_content,
            description="Batch normalization, layer normalization, internal covariate shift, training stability",
            difficulty=4,
            x_pos=6,
            y_pos=22,
            icon="⚖️",
            color="#8b5cf6",
            parent_ids=parent_ids
        )

        print("=" * 80)
        print("✓ Chapters 7-8 indexing completed successfully!")
        print()
        print("Topics added:")
        print("  Gradient Descent and Optimization")
        print("  Backpropagation Algorithm")
        print("  Advanced Optimizers (Adam, RMSprop, Momentum)")
        print("  Batch Normalization and Layer Normalization")
        print()
        print("Verify with:")
        print("  python scripts/check_indexed_content.py | grep -i 'gradient\\|backprop\\|adam'")

    except Exception as e:
        print(f"Error during indexing: {e}")
        import traceback
        traceback.print_exc()

    finally:
        indexer.close()


if __name__ == "__main__":
    main()
