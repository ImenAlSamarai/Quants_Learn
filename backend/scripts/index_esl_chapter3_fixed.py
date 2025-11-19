"""
Fixed Chapter 3 Indexing - Uses actual section structure from PDF

Changes from original:
- Extract full sections (3.2, 3.3, 3.4) instead of non-existent subsections
- Split section 3.4 into Ridge and Lasso by keyword search
- More robust content extraction
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


class Chapter3IndexerFixed:
    """Fixed indexer that matches actual PDF structure"""

    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.db = SessionLocal()
        self.extractor = ESLBookExtractor(pdf_path)
        self.chunk_size = settings.CHUNK_SIZE
        self.chunk_overlap = settings.CHUNK_OVERLAP

    def split_text(self, text: str) -> list:
        """Split text into overlapping chunks"""
        text = re.sub(r'\n\s*\n', '\n\n', text)
        paragraphs = text.split('\n\n')

        chunks = []
        current_chunk = ""

        for para in paragraphs:
            if len(current_chunk) + len(para) > self.chunk_size and current_chunk:
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
            start_section: Section to start from (e.g., "3.2")
            end_section: Section to end at (e.g., "3.3"), or None for end of chapter
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

    def extract_section_3_4_parts(self, chapter_text: str):
        """
        Split section 3.4 into Ridge (first half) and Lasso (second half)

        Section 3.4 covers "Shrinkage Methods" which includes both.
        We'll split at the point where Lasso is introduced.
        """
        # Extract full section 3.4
        section_3_4 = self.extract_section_range(chapter_text, "3.4", "3.5")

        if not section_3_4:
            return "", ""

        # Look for where Lasso section starts
        # The Lasso is typically introduced with a heading or "The lasso"
        lines = section_3_4.split('\n')

        lasso_start_idx = None
        for i, line in enumerate(lines):
            # Look for "lasso" as a major topic introduction
            if re.search(r'(The Lasso|3\.4\.2.*[Ll]asso)', line, re.IGNORECASE):
                lasso_start_idx = i
                break
            # Also check for common lasso equation introduction
            if 'lasso estimate' in line.lower() and i > len(lines) // 3:
                lasso_start_idx = i
                break

        if lasso_start_idx:
            ridge_content = '\n'.join(lines[:lasso_start_idx])
            lasso_content = '\n'.join(lines[lasso_start_idx:])
            return ridge_content, lasso_content
        else:
            # If we can't find split point, split roughly in half
            # Ridge is typically first half, Lasso second half
            mid_point = len(lines) // 2
            ridge_content = '\n'.join(lines[:mid_point])
            lasso_content = '\n'.join(lines[mid_point:])
            print("Warning: Splitting section 3.4 at midpoint (couldn't find Lasso heading)")
            return ridge_content, lasso_content

    def index_node(
        self,
        title: str,
        content: str,
        category: str = "machine_learning",
        subcategory: str = "regression",
        description: str = None,
        difficulty: int = 3,
        x_pos: float = 0,
        y_pos: float = 0,
        color: str = "#a78bfa",
        icon: str = "📈",
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
                content_path=f"esl_chapter3_{slug}"
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
                    'source': 'Elements of Statistical Learning, Chapter 3',
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

    parser = argparse.ArgumentParser(description="Index Chapter 3 from ESL (Fixed)")
    parser.add_argument('--init-db', action='store_true', help='Initialize database')
    parser.add_argument('--pdf-path', default='../content/machine_learning/elements_of_statistical_learning.pdf')
    args = parser.parse_args()

    if args.init_db:
        print("Initializing database...")
        init_db()
        print()

    indexer = Chapter3IndexerFixed(args.pdf_path)

    print("=" * 80)
    print("Fixed Chapter 3 Indexing - Using Actual PDF Structure")
    print("=" * 80)
    print()

    # Extract chapter once
    chapter_data = indexer.extractor.extract_chapter(3)

    if not chapter_data:
        print("Failed to extract Chapter 3!")
        indexer.close()
        return

    chapter_text = chapter_data['text']
    print(f"Chapter 3 extracted: {len(chapter_text):,} characters")
    print()

    # Find parent nodes
    regression_parent = indexer.db.query(Node).filter(Node.title == "Regression Analysis").first()
    stats_root = indexer.db.query(Node).filter(Node.title == "Statistics").first()

    parent_ids = []
    if regression_parent:
        parent_ids.append(regression_parent.id)
        print(f"✓ Found parent: Regression Analysis (ID: {regression_parent.id})")
    if stats_root:
        parent_ids.append(stats_root.id)
        print(f"✓ Found parent: Statistics (ID: {stats_root.id})")
    print()

    try:
        # Topic 1: Linear Regression (Section 3.2)
        print("[1/4] Indexing: Linear Regression and Least Squares")
        section_3_2 = indexer.extract_section_range(chapter_text, "3.2", "3.3")
        indexer.index_node(
            title="Linear Regression and Least Squares",
            content=section_3_2,
            description="Ordinary least squares estimation, Gauss-Markov theorem, and geometric interpretation",
            difficulty=3,
            x_pos=0,
            y_pos=6,
            icon="📐",
            parent_ids=parent_ids
        )

        # Topic 2: Subset Selection (Section 3.3)
        print("[2/4] Indexing: Subset Selection Methods")
        section_3_3 = indexer.extract_section_range(chapter_text, "3.3", "3.4")
        indexer.index_node(
            title="Subset Selection Methods",
            content=section_3_3,
            description="Best subset selection, forward and backward stepwise selection",
            difficulty=3,
            x_pos=-3,
            y_pos=8,
            icon="🔍",
            parent_ids=parent_ids
        )

        # Topic 3 & 4: Split Section 3.4 into Ridge and Lasso
        print("[3/4] Extracting Ridge Regression from Section 3.4...")
        ridge_content, lasso_content = indexer.extract_section_3_4_parts(chapter_text)

        indexer.index_node(
            title="Ridge Regression",
            content=ridge_content,
            description="L2 regularization, bias-variance tradeoff, and shrinkage",
            difficulty=3,
            x_pos=0,
            y_pos=8,
            icon="🏔️",
            parent_ids=parent_ids
        )

        print("[4/4] Indexing: Lasso Regression from Section 3.4...")
        indexer.index_node(
            title="Lasso Regression",
            content=lasso_content,
            description="L1 regularization, sparse solutions, and variable selection",
            difficulty=4,
            x_pos=3,
            y_pos=8,
            icon="🎯",
            parent_ids=parent_ids
        )

        print("=" * 80)
        print("✓ Chapter 3 indexing completed successfully!")
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
