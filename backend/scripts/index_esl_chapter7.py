"""
Index Chapter 7 from Elements of Statistical Learning: Model Assessment and Selection

Creates topics:
1. Cross-Validation Methods
2. Bootstrap Methods
3. Bias-Variance Decomposition
4. Model Selection Criteria

CRITICAL for quant researchers to avoid overfitting in backtesting.
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


class Chapter7Indexer:
    """Indexer for Chapter 7: Model Assessment and Selection"""

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

        # Split by paragraphs first
        paragraphs = text.split('\n\n')

        chunks = []
        current_chunk = ""

        for para in paragraphs:
            # If single paragraph is too long, split it by sentences
            if len(para) > max_chunk_chars:
                # Split long paragraph into sentences
                sentences = re.split(r'(?<=[.!?])\s+', para)
                for sentence in sentences:
                    if len(current_chunk) + len(sentence) > max_chunk_chars and current_chunk:
                        chunks.append(current_chunk.strip())
                        # Add overlap
                        words = current_chunk.split()
                        overlap_words = words[-self.chunk_overlap:] if len(words) > self.chunk_overlap else words
                        current_chunk = ' '.join(overlap_words) + ' ' + sentence
                    else:
                        current_chunk += ' ' + sentence if current_chunk else sentence

                    # Hard limit: if current chunk exceeds max, force save it
                    if len(current_chunk) > max_chunk_chars:
                        chunks.append(current_chunk.strip())
                        current_chunk = ""
            else:
                # Normal paragraph processing
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

    def extract_section_range(self, chapter_text: str, start_section: str, end_section: str = None) -> str:
        """
        Extract content between two section markers

        Args:
            chapter_text: Full chapter text
            start_section: Section to start from (e.g., "7.1")
            end_section: Section to end at (e.g., "7.2"), or None for end of chapter
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
        subcategory: str = "model_selection",
        description: str = None,
        difficulty: int = 3,
        x_pos: float = 0,
        y_pos: float = 0,
        color: str = "#fb923c",
        icon: str = "🔬",
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
                content_path=f"esl_chapter7_{slug}"
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
                    'source': 'Elements of Statistical Learning, Chapter 7',
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

    parser = argparse.ArgumentParser(description="Index Chapter 7 from ESL")
    parser.add_argument('--init-db', action='store_true', help='Initialize database')
    parser.add_argument('--pdf-path', default='../content/machine_learning/elements_of_statistical_learning.pdf')
    args = parser.parse_args()

    if args.init_db:
        print("Initializing database...")
        init_db()
        print()

    indexer = Chapter7Indexer(args.pdf_path)

    print("=" * 80)
    print("Chapter 7 Indexing: Model Assessment and Selection")
    print("=" * 80)
    print()

    # Extract chapter once
    chapter_data = indexer.extractor.extract_chapter(7)

    if not chapter_data:
        print("Failed to extract Chapter 7!")
        indexer.close()
        return

    chapter_text = chapter_data['text']
    print(f"Chapter 7 extracted: {len(chapter_text):,} characters")
    print()

    # Display sections found
    print("Sections found:")
    for section in chapter_data['sections']:
        print(f"  {section['number']} {section['title']}")
    print()

    # Find parent nodes
    stats_root = indexer.db.query(Node).filter(Node.title == "Statistics").first()
    ml_category = indexer.db.query(Node).filter(Node.category == "machine_learning").first()

    parent_ids = []
    if stats_root:
        parent_ids.append(stats_root.id)
        print(f"✓ Found parent: Statistics (ID: {stats_root.id})")
    print()

    try:
        # Topic 1: Bias-Variance Decomposition (Section 7.3)
        print("[1/4] Indexing: Bias-Variance Decomposition")
        section_7_3 = indexer.extract_section_range(chapter_text, "7.3", "7.4")
        indexer.index_node(
            title="Bias-Variance Decomposition",
            content=section_7_3,
            description="Understanding the bias-variance tradeoff, connection to model complexity and overfitting",
            difficulty=3,
            x_pos=-4,
            y_pos=12,
            icon="⚖️",
            color="#fb923c",
            parent_ids=parent_ids
        )

        # Topic 2: Cross-Validation (Section 7.10)
        print("[2/4] Indexing: Cross-Validation Methods")
        section_7_10 = indexer.extract_section_range(chapter_text, "7.10", "7.11")
        indexer.index_node(
            title="Cross-Validation Methods",
            content=section_7_10,
            description="K-fold cross-validation, leave-one-out CV, time series cross-validation for trading strategy backtesting",
            difficulty=3,
            x_pos=-1.5,
            y_pos=12,
            icon="🔄",
            color="#fb923c",
            parent_ids=parent_ids
        )

        # Topic 3: Bootstrap Methods (Section 7.11)
        print("[3/4] Indexing: Bootstrap Methods")
        section_7_11 = indexer.extract_section_range(chapter_text, "7.11", "7.12")

        # If 7.11 not found or too short, try 7.8
        if not section_7_11 or len(section_7_11) < 1000:
            print("  Note: Section 7.11 not found, trying 7.8...")
            section_7_11 = indexer.extract_section_range(chapter_text, "7.8", "7.9")

        indexer.index_node(
            title="Bootstrap Methods",
            content=section_7_11,
            description="Bootstrap confidence intervals, hypothesis testing, resampling for risk estimation",
            difficulty=4,
            x_pos=1.5,
            y_pos=12,
            icon="🎲",
            color="#fb923c",
            parent_ids=parent_ids
        )

        # Topic 4: Model Selection Criteria (Sections 7.4-7.7)
        print("[4/4] Indexing: Model Selection Criteria")
        # Extract multiple sections for comprehensive coverage
        section_7_4 = indexer.extract_section_range(chapter_text, "7.4", "7.5")
        section_7_5 = indexer.extract_section_range(chapter_text, "7.5", "7.6")
        section_7_6 = indexer.extract_section_range(chapter_text, "7.6", "7.7")
        section_7_7 = indexer.extract_section_range(chapter_text, "7.7", "7.8")

        combined_content = '\n\n'.join([s for s in [section_7_4, section_7_5, section_7_6, section_7_7] if s])

        indexer.index_node(
            title="Model Selection Criteria",
            content=combined_content,
            description="AIC, BIC, Cp, cross-validation error, test set validation for choosing between competing models",
            difficulty=4,
            x_pos=4,
            y_pos=12,
            icon="🎯",
            color="#fb923c",
            parent_ids=parent_ids
        )

        print("=" * 80)
        print("✓ Chapter 7 indexing completed successfully!")
        print()
        print("Verify with:")
        print("  python scripts/check_indexed_content.py")
        print("  python scripts/demonstrate_rag.py")

    except Exception as e:
        print(f"Error during indexing: {e}")
        import traceback
        traceback.print_exc()

    finally:
        indexer.close()


if __name__ == "__main__":
    main()
