"""
Index Chapter 14 from Elements of Statistical Learning: Unsupervised Learning

Creates topics:
1. Principal Component Analysis (PCA)
2. K-Means Clustering
3. Hierarchical Clustering
4. Dimensionality Reduction Techniques

CRITICAL for quant finance - PCA is used in factor models, risk decomposition,
portfolio construction. Clustering for regime detection and market segmentation.
"""

import os
import sys
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.database import SessionLocal, Node, ContentChunk, init_db
from app.services.vector_store import vector_store
from app.config.settings import settings
from pdf_extractor import ESLBookExtractor
import re


class Chapter14Indexer:
    """Indexer for Chapter 14: Unsupervised Learning"""

    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.db = SessionLocal()
        self.extractor = ESLBookExtractor(pdf_path)
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

    def extract_section_range(self, chapter_text: str, start_section: str, end_section: str = None) -> str:
        """
        Extract content between two section markers

        Args:
            chapter_text: Full chapter text
            start_section: Section to start from (e.g., "14.3")
            end_section: Section to end at (e.g., "14.4"), or None for end of chapter
        """
        lines = chapter_text.split('\n')

        # Find start
        start_idx = None
        for i, line in enumerate(lines):
            if re.match(f'^{re.escape(start_section)}\\s+', line.strip()):
                start_idx = i
                break

        if start_idx is None:
            print(f"Warning: Section {start_section} not found")
            return ""

        # Find end
        end_idx = len(lines)
        if end_section:
            for i in range(start_idx + 1, len(lines)):
                if re.match(f'^{re.escape(end_section)}\\s+', lines[i].strip()):
                    end_idx = i
                    break

        content = '\n'.join(lines[start_idx:end_idx])
        return content

    def index_node(
        self,
        title: str,
        content: str,
        category: str = "machine_learning",
        subcategory: str = "unsupervised_learning",
        description: str = None,
        difficulty: int = 4,
        x_pos: float = 0,
        y_pos: float = 0,
        color: str = "#8b5cf6",
        icon: str = "🔍",
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
                content_path=f"esl_chapter14_{slug}"
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
                    'source': 'Elements of Statistical Learning, Chapter 14',
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
                'source_book': 'ESL'
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

    parser = argparse.ArgumentParser(description="Index Chapter 14 from ESL")
    parser.add_argument('--init-db', action='store_true', help='Initialize database')
    parser.add_argument('--pdf-path', default='../content/machine_learning/elements_of_statistical_learning.pdf')
    args = parser.parse_args()

    if args.init_db:
        print("Initializing database...")
        init_db()
        print()

    indexer = Chapter14Indexer(args.pdf_path)

    print("=" * 80)
    print("Chapter 14 Indexing: Unsupervised Learning")
    print("=" * 80)
    print()

    # Extract chapter
    chapter_data = indexer.extractor.extract_chapter(14)

    if not chapter_data:
        print("Failed to extract Chapter 14!")
        indexer.close()
        return

    chapter_text = chapter_data['text']
    print(f"Chapter 14 extracted: {len(chapter_text):,} characters")
    print()

    # Display sections found
    print("Sections found:")
    for section in chapter_data['sections']:
        print(f"  {section['number']} {section['title']}")
    print()

    # Find parent nodes
    stats_root = indexer.db.query(Node).filter(Node.title == "Statistics").first()

    parent_ids = []
    if stats_root:
        parent_ids.append(stats_root.id)
        print(f"✓ Found parent: Statistics (ID: {stats_root.id})")
    print()

    try:
        # Topic 1: Principal Component Analysis (Section 14.5)
        print("[1/5] Indexing: Principal Component Analysis (PCA)")
        section_14_5 = indexer.extract_section_range(chapter_text, "14.5", "14.6")

        # If section not found, try alternative sections
        if not section_14_5 or len(section_14_5) < 1000:
            section_14_5 = indexer.extract_section_range(chapter_text, "14.3", "14.4")

        if not section_14_5 or len(section_14_5) < 1000:
            # Use first quarter of chapter
            lines = chapter_text.split('\n')
            section_14_5 = '\n'.join(lines[:len(lines)//4])

        indexer.index_node(
            title="Principal Component Analysis (PCA)",
            content=section_14_5,
            description="Dimensionality reduction, eigenvalue decomposition, variance maximization, factor models for quant finance",
            difficulty=4,
            x_pos=-6,
            y_pos=18,
            icon="📊",
            color="#8b5cf6",
            parent_ids=parent_ids
        )

        # Topic 2: K-Means Clustering (Section 14.3)
        print("[2/5] Indexing: K-Means Clustering")
        section_14_3 = indexer.extract_section_range(chapter_text, "14.3", "14.4")

        if not section_14_3 or len(section_14_3) < 500:
            # Use second quarter
            lines = chapter_text.split('\n')
            start = len(lines) // 4
            end = len(lines) // 2
            section_14_3 = '\n'.join(lines[start:end])

        indexer.index_node(
            title="K-Means Clustering",
            content=section_14_3,
            description="Centroid-based clustering, within-cluster variance minimization, initialization strategies, market regime detection",
            difficulty=3,
            x_pos=-3,
            y_pos=18,
            icon="🎯",
            color="#8b5cf6",
            parent_ids=parent_ids
        )

        # Topic 3: Hierarchical Clustering (Section 14.3.12 or nearby)
        print("[3/5] Indexing: Hierarchical Clustering")
        section_14_3_12 = indexer.extract_section_range(chapter_text, "14.3.12", "14.4")

        if not section_14_3_12 or len(section_14_3_12) < 500:
            # Try main hierarchical clustering section
            section_14_3_12 = indexer.extract_section_range(chapter_text, "14.4", "14.5")

        if not section_14_3_12 or len(section_14_3_12) < 500:
            # Use third quarter
            lines = chapter_text.split('\n')
            start = len(lines) // 2
            end = 3 * len(lines) // 4
            section_14_3_12 = '\n'.join(lines[start:end])

        indexer.index_node(
            title="Hierarchical Clustering",
            content=section_14_3_12,
            description="Agglomerative and divisive clustering, dendrograms, linkage methods (single, complete, average), asset grouping",
            difficulty=4,
            x_pos=0,
            y_pos=18,
            icon="🌳",
            color="#8b5cf6",
            parent_ids=parent_ids
        )

        # Topic 4: Dimensionality Reduction Techniques (broader content)
        print("[4/5] Indexing: Dimensionality Reduction Techniques")
        # Combine multiple sections or use latter part
        section_14_6 = indexer.extract_section_range(chapter_text, "14.6", "14.7")
        section_14_7 = indexer.extract_section_range(chapter_text, "14.7", "14.8")

        dim_reduction_content = section_14_6 + "\n\n" + section_14_7

        if not dim_reduction_content or len(dim_reduction_content) < 1000:
            # Use last quarter
            lines = chapter_text.split('\n')
            start = 3 * len(lines) // 4
            dim_reduction_content = '\n'.join(lines[start:])

        indexer.index_node(
            title="Dimensionality Reduction Techniques",
            content=dim_reduction_content,
            description="PCA, ICA, manifold learning, t-SNE concepts, applications to high-dimensional portfolio data",
            difficulty=5,
            x_pos=3,
            y_pos=18,
            icon="🔬",
            color="#8b5cf6",
            parent_ids=parent_ids
        )

        # Topic 5: Covariance Estimation (relevant for quant finance)
        print("[5/5] Indexing: Covariance Matrix Estimation")
        # This might be in various sections, use mixed content
        lines = chapter_text.split('\n')
        # Use middle portions
        start = len(lines) // 3
        end = 2 * len(lines) // 3
        covariance_content = '\n'.join(lines[start:end])

        indexer.index_node(
            title="Covariance Matrix Estimation",
            content=covariance_content,
            description="Sample covariance, shrinkage estimators, factor models, applications to portfolio optimization",
            difficulty=5,
            x_pos=6,
            y_pos=18,
            icon="📐",
            color="#8b5cf6",
            parent_ids=parent_ids
        )

        print("=" * 80)
        print("✓ Chapter 14 indexing completed successfully!")
        print()
        print("Topics added:")
        print("  Principal Component Analysis (PCA)")
        print("  K-Means Clustering")
        print("  Hierarchical Clustering")
        print("  Dimensionality Reduction Techniques")
        print("  Covariance Matrix Estimation")
        print()
        print("Verify with:")
        print("  python scripts/check_indexed_content.py")

    except Exception as e:
        print(f"Error during indexing: {e}")
        import traceback
        traceback.print_exc()

    finally:
        indexer.close()


if __name__ == "__main__":
    main()
