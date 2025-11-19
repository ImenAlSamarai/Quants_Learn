"""
Index Chapters 9 & 10 from Elements of Statistical Learning: Tree-Based Methods

Creates topics:
Chapter 9 - Trees and Additive Models:
1. Decision Trees (CART)
2. Regression and Classification Trees
3. Tree Pruning Methods

Chapter 10 - Boosting:
4. AdaBoost Algorithm
5. Gradient Boosting Machines
6. Boosting vs Bagging

CRITICAL for ML interviews at hedge funds - tree methods are heavily used in trading.
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


class Chapters9_10_Indexer:
    """Indexer for Chapters 9 & 10: Tree-Based Methods and Boosting"""

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
            start_section: Section to start from (e.g., "9.2")
            end_section: Section to end at (e.g., "9.3"), or None for end of chapter
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
        subcategory: str = "tree_methods",
        description: str = None,
        difficulty: int = 4,
        x_pos: float = 0,
        y_pos: float = 0,
        color: str = "#10b981",
        icon: str = "🌳",
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
                content_path=f"esl_chapters_9_10_{slug}"
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
                    'source': 'Elements of Statistical Learning, Chapters 9-10',
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

    parser = argparse.ArgumentParser(description="Index Chapters 9 & 10 from ESL")
    parser.add_argument('--init-db', action='store_true', help='Initialize database')
    parser.add_argument('--pdf-path', default='../content/machine_learning/elements_of_statistical_learning.pdf')
    args = parser.parse_args()

    if args.init_db:
        print("Initializing database...")
        init_db()
        print()

    indexer = Chapters9_10_Indexer(args.pdf_path)

    print("=" * 80)
    print("Chapters 9-10 Indexing: Tree-Based Methods and Boosting")
    print("=" * 80)
    print()

    # Extract both chapters
    chapter_9_data = indexer.extractor.extract_chapter(9)
    chapter_10_data = indexer.extractor.extract_chapter(10)

    if not chapter_9_data or not chapter_10_data:
        print("Failed to extract chapters!")
        indexer.close()
        return

    chapter_9_text = chapter_9_data['text']
    chapter_10_text = chapter_10_data['text']

    print(f"Chapter 9 extracted: {len(chapter_9_text):,} characters")
    print(f"Chapter 10 extracted: {len(chapter_10_text):,} characters")
    print()

    # Display sections
    print("Chapter 9 sections:")
    for section in chapter_9_data['sections']:
        print(f"  {section['number']} {section['title']}")
    print()

    print("Chapter 10 sections:")
    for section in chapter_10_data['sections']:
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
        # === CHAPTER 9: Trees ===

        # Topic 1: Decision Trees CART (Section 9.2)
        print("[1/6] Indexing: Decision Trees (CART)")
        section_9_2 = indexer.extract_section_range(chapter_9_text, "9.2", "9.3")
        indexer.index_node(
            title="Decision Trees (CART)",
            content=section_9_2,
            description="Classification and Regression Trees - tree growing, splitting rules, impurity measures (Gini, entropy)",
            difficulty=4,
            x_pos=-6,
            y_pos=14,
            icon="🌲",
            color="#10b981",
            parent_ids=parent_ids
        )

        # Topic 2: Regression Trees
        print("[2/6] Indexing: Regression Trees")
        # Get early part of 9.2 or use intro sections
        section_9_2_full = indexer.extract_section_range(chapter_9_text, "9.2", "9.3")
        # Split approximately in half for regression vs classification
        lines = section_9_2_full.split('\n')
        half = len(lines) // 2
        regression_trees_content = '\n'.join(lines[:half])

        indexer.index_node(
            title="Regression Trees",
            content=regression_trees_content,
            description="Tree-based regression, continuous target prediction, split point selection, terminal node predictions",
            difficulty=4,
            x_pos=-3,
            y_pos=14,
            icon="📊",
            color="#10b981",
            parent_ids=parent_ids
        )

        # Topic 3: Tree Pruning (Section 9.2 later parts or general content)
        print("[3/6] Indexing: Tree Pruning Methods")
        # Extract from later parts or use combined sections
        section_9_3_onwards = indexer.extract_section_range(chapter_9_text, "9.3", "9.4")

        if not section_9_3_onwards or len(section_9_3_onwards) < 1000:
            # Fall back to using latter half of chapter
            lines = chapter_9_text.split('\n')
            start_line = int(len(lines) * 0.5)
            section_9_3_onwards = '\n'.join(lines[start_line:])

        indexer.index_node(
            title="Tree Pruning Methods",
            content=section_9_3_onwards,
            description="Cost-complexity pruning, cross-validation for tree size selection, avoiding overfitting in trees",
            difficulty=4,
            x_pos=0,
            y_pos=14,
            icon="✂️",
            color="#10b981",
            parent_ids=parent_ids
        )

        # === CHAPTER 10: Boosting ===

        # Topic 4: AdaBoost (Section 10.1)
        print("[4/6] Indexing: AdaBoost Algorithm")
        section_10_1 = indexer.extract_section_range(chapter_10_text, "10.1", "10.2")

        if not section_10_1 or len(section_10_1) < 1000:
            # Use first third of chapter
            lines = chapter_10_text.split('\n')
            section_10_1 = '\n'.join(lines[:len(lines)//3])

        indexer.index_node(
            title="AdaBoost Algorithm",
            content=section_10_1,
            description="Adaptive Boosting - sequential weak learners, exponential loss, weighted voting, margin theory",
            difficulty=4,
            x_pos=3,
            y_pos=14,
            icon="🚀",
            color="#10b981",
            parent_ids=parent_ids
        )

        # Topic 5: Gradient Boosting (Section 10.10 or main gradient boosting sections)
        print("[5/6] Indexing: Gradient Boosting Machines")
        section_10_10 = indexer.extract_section_range(chapter_10_text, "10.10", "10.11")

        # If section not found, try other section numbers
        if not section_10_10 or len(section_10_10) < 1000:
            section_10_10 = indexer.extract_section_range(chapter_10_text, "10.9", "10.10")

        if not section_10_10 or len(section_10_10) < 1000:
            # Use middle third of chapter
            lines = chapter_10_text.split('\n')
            start = len(lines) // 3
            end = 2 * len(lines) // 3
            section_10_10 = '\n'.join(lines[start:end])

        indexer.index_node(
            title="Gradient Boosting Machines",
            content=section_10_10,
            description="GBM, gradient descent in function space, shrinkage, tree depth, XGBoost foundations",
            difficulty=5,
            x_pos=6,
            y_pos=14,
            icon="⚡",
            color="#10b981",
            parent_ids=parent_ids
        )

        # Topic 6: Boosting vs Bagging
        print("[6/6] Indexing: Boosting vs Bagging")
        # Use latter part of chapter or combined content
        lines = chapter_10_text.split('\n')
        start_line = 2 * len(lines) // 3
        boosting_vs_bagging_content = '\n'.join(lines[start_line:])

        indexer.index_node(
            title="Boosting vs Bagging",
            content=boosting_vs_bagging_content,
            description="Ensemble methods comparison - variance reduction vs bias reduction, random forests connection",
            difficulty=4,
            x_pos=9,
            y_pos=14,
            icon="⚖️",
            color="#10b981",
            parent_ids=parent_ids
        )

        print("=" * 80)
        print("✓ Chapters 9-10 indexing completed successfully!")
        print()
        print("Topics added:")
        print("  [Ch 9] Decision Trees (CART)")
        print("  [Ch 9] Regression Trees")
        print("  [Ch 9] Tree Pruning Methods")
        print("  [Ch 10] AdaBoost Algorithm")
        print("  [Ch 10] Gradient Boosting Machines")
        print("  [Ch 10] Boosting vs Bagging")
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
