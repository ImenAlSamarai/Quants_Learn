"""
Index Chapter 3 from Elements of Statistical Learning

This script creates nodes for key topics in Chapter 3 and indexes
the content into the vector store for RAG retrieval.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.database import SessionLocal, Node, ContentChunk, init_db
from app.services.vector_store import vector_store
from app.config.settings import settings
from pdf_extractor import ESLBookExtractor
import re


class Chapter3Indexer:
    """Index Chapter 3: Linear Methods for Regression"""

    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.db = SessionLocal()
        self.extractor = ESLBookExtractor(pdf_path)
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

                # Start new chunk with overlap
                words = current_chunk.split()
                overlap_words = words[-self.chunk_overlap:] if len(words) > self.chunk_overlap else words
                current_chunk = ' '.join(overlap_words) + '\n\n' + para
            else:
                current_chunk += '\n\n' + para if current_chunk else para

        # Add the last chunk
        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def extract_section_content(self, chapter_text: str, section_number: str) -> str:
        """
        Extract content for a specific section from chapter text

        Args:
            chapter_text: Full chapter text
            section_number: Section number like "3.2" or "3.4.3"

        Returns:
            Section content
        """
        # Find the section start
        pattern = f"^{re.escape(section_number)}\\s+"
        lines = chapter_text.split('\n')

        start_idx = None
        for i, line in enumerate(lines):
            if re.match(pattern, line.strip()):
                start_idx = i
                break

        if start_idx is None:
            print(f"Warning: Section {section_number} not found")
            return ""

        # Find the next section (to know where this section ends)
        # Next section will be same depth or higher (e.g., 3.3 after 3.2, or 3.2.1 after 3.2)
        section_depth = section_number.count('.')
        next_section_pattern = r'^3\.\d+'

        end_idx = len(lines)
        for i in range(start_idx + 1, len(lines)):
            if re.match(next_section_pattern, lines[i].strip()):
                # Check if this is a next section at same or higher level
                next_num = lines[i].strip().split()[0]
                if next_num.count('.') <= section_depth:
                    end_idx = i
                    break

        section_content = '\n'.join(lines[start_idx:end_idx])
        return section_content

    def index_node(
        self,
        title: str,
        section_numbers: list,
        category: str = "machine_learning",
        subcategory: str = "regression",
        description: str = None,
        difficulty: int = 3,
        x_pos: float = 0,
        y_pos: float = 0,
        color: str = "#8b5cf6",
        icon: str = "📈",
        parent_ids: list = None
    ):
        """
        Index a topic from Chapter 3

        Args:
            title: Node title
            section_numbers: List of section numbers to extract (e.g., ["3.2", "3.2.1"])
            category: Content category
            subcategory: Content subcategory
            description: Node description
            difficulty: Difficulty level (1-5)
            x_pos: X position in mind map
            y_pos: Y position in mind map
            color: Node color
            icon: Node icon
            parent_ids: Parent node IDs
        """
        # Create slug from title
        slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')

        # Check if node already exists
        existing_node = self.db.query(Node).filter(Node.slug == slug).first()

        if existing_node:
            print(f"Node '{title}' already exists. Updating...")
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
                content_path=f"esl_chapter3_{slug}"  # Virtual path
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

        # Extract and index content
        print(f"Extracting content for sections: {section_numbers}")
        chapter_data = self.extractor.extract_chapter(3)

        if not chapter_data:
            print("Error: Could not extract Chapter 3")
            return None

        # Combine content from all specified sections
        combined_content = []
        for section_num in section_numbers:
            section_content = self.extract_section_content(chapter_data['text'], section_num)
            if section_content:
                combined_content.append(f"Section {section_num}:\n{section_content}")

        full_content = "\n\n".join(combined_content)

        if not full_content.strip():
            print(f"Warning: No content extracted for {title}")
            return node.id

        # Split into chunks
        chunks = self.split_text(full_content)
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
                    'difficulty': difficulty,
                    'source': 'Elements of Statistical Learning, Chapter 3',
                    'sections': ', '.join(section_numbers)
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
        print(f"✓ Indexed {len(chunks)} chunks for '{title}'")
        print()

        return node.id

    def close(self):
        """Close connections"""
        self.db.close()
        self.extractor.close()


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Index Chapter 3 from ESL")
    parser.add_argument('--init-db', action='store_true', help='Initialize database')
    parser.add_argument('--pdf-path', default='../content/machine_learning/elements_of_statistical_learning.pdf')
    args = parser.parse_args()

    # Initialize database if requested
    if args.init_db:
        print("Initializing database...")
        init_db()
        print()

    indexer = Chapter3Indexer(args.pdf_path)

    print("=" * 80)
    print("Indexing Chapter 3: Linear Methods for Regression")
    print("Elements of Statistical Learning (Hastie, Tibshirani, Friedman)")
    print("=" * 80)
    print()

    # Find parent nodes from existing content
    # These are the existing Statistics and Linear Algebra nodes
    regression_parent = indexer.db.query(Node).filter(Node.title == "Regression Analysis").first()
    stats_root = indexer.db.query(Node).filter(Node.title == "Statistics").first()
    la_root = indexer.db.query(Node).filter(Node.title == "Linear Algebra").first()

    parent_ids = []
    if regression_parent:
        parent_ids.append(regression_parent.id)
        print(f"✓ Found parent: Regression Analysis (ID: {regression_parent.id})")
    if stats_root:
        parent_ids.append(stats_root.id)
        print(f"✓ Found parent: Statistics (ID: {stats_root.id})")
    if la_root:
        print(f"✓ Found: Linear Algebra root (ID: {la_root.id})")

    print()

    try:
        # Topic 1: Linear Regression and Least Squares
        print("[1/4] Indexing: Linear Regression and Least Squares")
        linear_regression_id = indexer.index_node(
            title="Linear Regression and Least Squares",
            section_numbers=["3.2", "3.2.1", "3.2.2", "3.2.3"],
            description="Ordinary least squares estimation, Gauss-Markov theorem, and geometric interpretation",
            difficulty=3,
            x_pos=0,
            y_pos=6,
            color="#a78bfa",
            icon="📐",
            parent_ids=parent_ids
        )

        # Topic 2: Subset Selection
        print("[2/4] Indexing: Subset Selection Methods")
        subset_id = indexer.index_node(
            title="Subset Selection Methods",
            section_numbers=["3.3", "3.3.1", "3.3.2", "3.3.3"],
            description="Best subset selection, forward and backward stepwise selection, and model selection criteria",
            difficulty=3,
            x_pos=-3,
            y_pos=8,
            color="#a78bfa",
            icon="🔍",
            parent_ids=[linear_regression_id] if linear_regression_id else parent_ids
        )

        # Topic 3: Ridge Regression
        print("[3/4] Indexing: Ridge Regression")
        ridge_id = indexer.index_node(
            title="Ridge Regression",
            section_numbers=["3.4.1", "3.4.2"],
            description="L2 regularization, bias-variance tradeoff, and connection to Bayesian estimation",
            difficulty=3,
            x_pos=0,
            y_pos=8,
            color="#a78bfa",
            icon="🏔️",
            parent_ids=[linear_regression_id] if linear_regression_id else parent_ids
        )

        # Topic 4: Lasso Regression
        print("[4/4] Indexing: Lasso Regression")
        lasso_id = indexer.index_node(
            title="Lasso Regression",
            section_numbers=["3.4.2", "3.4.3", "3.4.4"],
            description="L1 regularization, sparse solutions, variable selection, and the LARS algorithm",
            difficulty=4,
            x_pos=3,
            y_pos=8,
            color="#a78bfa",
            icon="🎯",
            parent_ids=[linear_regression_id] if linear_regression_id else parent_ids
        )

        print("=" * 80)
        print("✓ Chapter 3 indexing completed successfully!")
        print()
        print("Topics indexed:")
        print("  1. Linear Regression and Least Squares")
        print("  2. Subset Selection Methods")
        print("  3. Ridge Regression")
        print("  4. Lasso Regression")
        print()
        print("Next steps:")
        print("  1. Start backend: python -m app.main")
        print("  2. Test RAG retrieval with one of the new topics")
        print("  3. Verify content generation adapts to difficulty levels")

    except Exception as e:
        print(f"Error during indexing: {e}")
        import traceback
        traceback.print_exc()

    finally:
        indexer.close()


if __name__ == "__main__":
    main()
