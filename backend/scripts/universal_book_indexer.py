"""
Universal Book/Document Indexer for Quants_Learn

STRATEGIC APPROACH:
- Scans all PDFs in content directory (any subfolder)
- Smart categorization: Books can belong to MULTIPLE categories (tags)
- Physical folder location doesn't dictate category
- Checks if content already indexed before processing
- Supports incremental updates without breaking existing content

USAGE:
    python scripts/universal_book_indexer.py --scan          # Scan and show what would be indexed
    python scripts/universal_book_indexer.py --index-new     # Index only new books
    python scripts/universal_book_indexer.py --reindex-all   # Reindex everything (careful!)
    python scripts/universal_book_indexer.py --book "advances_in_financial_ml.pdf"  # Index specific book

BOOK METADATA:
Define your books in BOOK_REGISTRY below with:
- pdf_filename: Name of PDF file
- title: Display title
- primary_category: Main category (machine_learning, statistics, etc.)
- secondary_categories: List of additional relevant categories
- chapters: List of chapter definitions for indexing
"""

import os
import sys
import argparse
from pathlib import Path
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.database import SessionLocal, Node, ContentChunk, init_db
from app.services.vector_store import vector_store
from app.config.settings import settings
from pdf_extractor import ESLBookExtractor
import fitz  # PyMuPDF


# ==================== BOOK REGISTRY ====================
# Add your books here with categorization metadata

BOOK_REGISTRY = {
    "elements_of_statistical_learning.pdf": {
        "title": "Elements of Statistical Learning",
        "short_name": "ESL",
        "authors": "Hastie, Tibshirani, Friedman",
        "primary_category": "machine_learning",
        "secondary_categories": ["statistics"],  # Cross-category tagging
        "description": "Comprehensive coverage of statistical learning methods",
        "extractor_class": "ESLBookExtractor",
        "chapters": [
            {"num": 3, "title": "Linear Methods for Regression", "subcategory": "regression", "difficulty": 3},
            {"num": 4, "title": "Linear Methods for Classification", "subcategory": "classification", "difficulty": 3},
            {"num": 7, "title": "Model Assessment and Selection", "subcategory": "model_selection", "difficulty": 4},
            {"num": 9, "title": "Additive Models, Trees", "subcategory": "tree_methods", "difficulty": 4},
            {"num": 10, "title": "Boosting and Additive Trees", "subcategory": "boosting", "difficulty": 4},
            {"num": 14, "title": "Unsupervised Learning", "subcategory": "unsupervised", "difficulty": 4},
            {"num": 15, "title": "Random Forests", "subcategory": "random_forests", "difficulty": 4},
        ]
    },

    "deep_learning_foundations_and_concepts.pdf": {
        "title": "Deep Learning: Foundations and Concepts",
        "short_name": "DL",
        "authors": "Bishop, Bishop",
        "primary_category": "machine_learning",
        "secondary_categories": ["deep_learning"],
        "description": "Modern deep learning theory and practice",
        "extractor_class": "GenericPDFExtractor",
        "chapters": [
            {"num": 6, "title": "Deep Neural Networks", "subcategory": "deep_learning", "difficulty": 4},
            {"num": 7, "title": "Convolutional Networks", "subcategory": "deep_learning", "difficulty": 4},
            {"num": 8, "title": "Graph Neural Networks", "subcategory": "deep_learning", "difficulty": 5},
            {"num": 10, "title": "Attention and Transformers", "subcategory": "deep_learning", "difficulty": 5},
            {"num": 12, "title": "Diffusion Models", "subcategory": "deep_learning", "difficulty": 5},
        ]
    },

    "bouchaud_book.pdf": {
        "title": "Theory of Financial Risk and Derivative Pricing",
        "short_name": "Bouchaud",
        "authors": "Bouchaud, Potters",
        "primary_category": "statistics",
        "secondary_categories": ["probability", "finance"],
        "description": "Statistical physics approach to financial markets",
        "extractor_class": "GenericPDFExtractor",
        "chapters": [
            {"num": 1, "title": "Heavy Tails and Fat Tails", "subcategory": "probability_distributions", "difficulty": 4},
        ]
    },

    # ⭐ ADD YOUR NEW BOOK HERE
    "advances_in_financial_ml.pdf": {
        "title": "Advances in Financial Machine Learning",
        "short_name": "AFML",
        "authors": "Marcos López de Prado",
        "primary_category": "finance",  # NEW category!
        "secondary_categories": ["machine_learning", "statistics"],  # Multiple tags
        "description": "Modern machine learning techniques for quantitative finance",
        "extractor_class": "GenericPDFExtractor",
        "chapters": [
            # Add chapter definitions as you index them
            # {"num": 1, "title": "Financial Data Structures", "subcategory": "data_engineering", "difficulty": 3},
            # {"num": 2, "title": "Backtesting", "subcategory": "validation", "difficulty": 4},
            # ... etc
        ]
    },
}


# ==================== EXTRACTORS ====================

class GenericPDFExtractor:
    """Generic PDF extractor for books without specific structure"""

    def __init__(self, pdf_path: str):
        self.pdf_path = Path(pdf_path)
        self.doc = fitz.open(str(self.pdf_path))
        self.total_pages = len(self.doc)

    def extract_text_from_pages(self, start_page: int, end_page: int) -> str:
        """Extract text from page range (0-indexed)"""
        text = []
        for page_num in range(start_page, min(end_page + 1, self.total_pages)):
            page = self.doc[page_num]
            page_text = page.get_text()
            text.append(page_text)
        return "\n".join(text)

    def extract_chapter(self, chapter_num: int, start_page: int = None, end_page: int = None) -> Optional[Dict]:
        """
        Extract chapter content

        Args:
            chapter_num: Chapter number
            start_page: Optional manual start page (0-indexed)
            end_page: Optional manual end page (0-indexed)
        """
        if start_page is None or end_page is None:
            # Try to auto-detect chapter pages
            pages = self._auto_detect_chapter_pages(chapter_num)
            if not pages:
                print(f"Warning: Could not auto-detect Chapter {chapter_num}. Please specify start_page and end_page.")
                return None
            start_page, end_page = pages

        text = self.extract_text_from_pages(start_page, end_page)

        return {
            'chapter_num': chapter_num,
            'title': f"Chapter {chapter_num}",
            'start_page': start_page + 1,
            'end_page': end_page + 1,
            'page_count': end_page - start_page + 1,
            'text': text,
        }

    def _auto_detect_chapter_pages(self, chapter_num: int) -> Optional[Tuple[int, int]]:
        """
        Attempt to auto-detect chapter page ranges
        Override this method for specific books
        """
        # Search for chapter headings
        for page_num in range(self.total_pages):
            page_text = self.doc[page_num].get_text()
            # Look for patterns like "Chapter 1", "1.", "Chapter One", etc.
            if re.search(f"Chapter\\s+{chapter_num}\\b", page_text, re.IGNORECASE):
                # Found start, now find end (next chapter or end of book)
                end_page = self.total_pages - 1
                for next_page in range(page_num + 1, self.total_pages):
                    next_text = self.doc[next_page].get_text()
                    if re.search(f"Chapter\\s+{chapter_num + 1}\\b", next_text, re.IGNORECASE):
                        end_page = next_page - 1
                        break
                return (page_num, end_page)

        return None

    def close(self):
        """Close PDF document"""
        self.doc.close()


# ==================== UNIVERSAL INDEXER ====================

class UniversalBookIndexer:
    """Smart indexer that handles any book with flexible categorization"""

    def __init__(self):
        self.db = SessionLocal()
        self.chunk_size = settings.CHUNK_SIZE
        self.chunk_overlap = settings.CHUNK_OVERLAP
        self.indexed_count = 0
        self.skipped_count = 0
        self.error_count = 0

    def find_all_pdfs(self, content_dir: str = "../content") -> List[Path]:
        """Recursively find all PDFs in content directory"""
        content_path = Path(content_dir)
        return list(content_path.rglob("*.pdf"))

    def get_book_info(self, pdf_path: Path) -> Optional[Dict]:
        """Get book metadata from registry"""
        filename = pdf_path.name
        return BOOK_REGISTRY.get(filename)

    def is_book_indexed(self, book_short_name: str) -> bool:
        """Check if book has any indexed nodes in database"""
        # Check if any nodes exist with this book's source
        nodes = self.db.query(Node).filter(
            Node.description.like(f"%{book_short_name}%")
        ).all()

        # Also check if content chunks exist with generated content
        if nodes:
            for node in nodes:
                chunks = self.db.query(ContentChunk).filter(
                    ContentChunk.node_id == node.id
                ).first()
                if chunks:
                    return True

        return False

    def scan_books(self, content_dir: str = "../content") -> Dict:
        """Scan all PDFs and report status"""
        pdfs = self.find_all_pdfs(content_dir)

        report = {
            "total_pdfs": len(pdfs),
            "registered": [],
            "unregistered": [],
            "already_indexed": [],
            "ready_to_index": [],
        }

        for pdf_path in pdfs:
            book_info = self.get_book_info(pdf_path)

            if not book_info:
                report["unregistered"].append({
                    "path": str(pdf_path),
                    "filename": pdf_path.name
                })
                continue

            report["registered"].append({
                "path": str(pdf_path),
                "title": book_info["title"],
                "short_name": book_info["short_name"]
            })

            # Check if already indexed
            if self.is_book_indexed(book_info["short_name"]):
                report["already_indexed"].append({
                    "title": book_info["title"],
                    "short_name": book_info["short_name"]
                })
            else:
                report["ready_to_index"].append({
                    "title": book_info["title"],
                    "short_name": book_info["short_name"],
                    "chapters": len(book_info.get("chapters", []))
                })

        return report

    def print_scan_report(self, report: Dict):
        """Print formatted scan report"""
        print("\n" + "=" * 80)
        print("📚 UNIVERSAL BOOK INDEXER - SCAN REPORT")
        print("=" * 80)

        print(f"\n📊 Summary:")
        print(f"  Total PDFs found: {report['total_pdfs']}")
        print(f"  Registered books: {len(report['registered'])}")
        print(f"  Unregistered PDFs: {len(report['unregistered'])}")
        print(f"  Already indexed: {len(report['already_indexed'])}")
        print(f"  Ready to index: {len(report['ready_to_index'])}")

        if report["already_indexed"]:
            print(f"\n✅ Already Indexed ({len(report['already_indexed'])}):")
            for book in report["already_indexed"]:
                print(f"  ✓ {book['title']} ({book['short_name']})")

        if report["ready_to_index"]:
            print(f"\n🆕 Ready to Index ({len(report['ready_to_index'])}):")
            for book in report["ready_to_index"]:
                ch_count = book['chapters']
                print(f"  → {book['title']} ({book['short_name']}) - {ch_count} chapters defined")

        if report["unregistered"]:
            print(f"\n⚠️  Unregistered PDFs ({len(report['unregistered'])}):")
            print("   These PDFs are not in BOOK_REGISTRY. Add them to enable indexing.")
            for pdf in report["unregistered"]:
                print(f"  • {pdf['filename']}")

        print("\n" + "=" * 80)

    def split_text(self, text: str) -> List[str]:
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

    def index_book_chapter(
        self,
        book_info: Dict,
        chapter_info: Dict,
        pdf_path: Path,
        parent_ids: List[int] = None
    ) -> Optional[int]:
        """
        Index a single chapter from a book

        Returns:
            Node ID if successful, None otherwise
        """
        try:
            # Get appropriate extractor
            extractor_class_name = book_info.get("extractor_class", "GenericPDFExtractor")
            if extractor_class_name == "ESLBookExtractor":
                extractor = ESLBookExtractor(str(pdf_path))
            else:
                extractor = GenericPDFExtractor(str(pdf_path))

            # Extract chapter content
            chapter_data = extractor.extract_chapter(chapter_info["num"])

            if not chapter_data:
                print(f"  ⚠️  Could not extract Chapter {chapter_info['num']}")
                self.error_count += 1
                return None

            # Create node title
            title = f"{book_info['short_name']} - {chapter_info['title']}"
            slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')

            # Check if already exists
            existing_node = self.db.query(Node).filter(Node.slug == slug).first()

            if existing_node:
                print(f"  ℹ️  '{title}' already exists (Node ID: {existing_node.id})")
                self.skipped_count += 1
                return existing_node.id

            # Create new node with MULTI-CATEGORY support
            primary_cat = book_info["primary_category"]
            subcategory = chapter_info.get("subcategory", "general")

            # Store secondary categories in description metadata
            secondary_cats = ", ".join(book_info.get("secondary_categories", []))
            description = f"{book_info['title']} - {chapter_info['title']}. Tags: {secondary_cats}"

            node = Node(
                title=title,
                slug=slug,
                category=primary_cat,
                subcategory=subcategory,
                description=description,
                difficulty_level=chapter_info.get("difficulty", 3),
                x_position=0,  # TODO: Auto-layout
                y_position=0,
                color=self._get_category_color(primary_cat),
                icon=self._get_category_icon(primary_cat),
                content_path=str(pdf_path)
            )

            self.db.add(node)
            self.db.commit()
            self.db.refresh(node)

            print(f"  ✅ Created node: {title} (ID: {node.id})")

            # Add parent relationships
            if parent_ids:
                parents = self.db.query(Node).filter(Node.id.in_(parent_ids)).all()
                node.parents = parents
                self.db.commit()

            # Index content into vector store
            text = chapter_data.get('text', '')
            chunks = self.split_text(text)

            print(f"    → Indexing {len(chunks)} chunks into Pinecone...")

            # Delete existing chunks
            self.db.query(ContentChunk).filter(ContentChunk.node_id == node.id).delete()
            vector_store.delete_node_vectors(node.id)

            # Prepare chunk data with multi-category metadata
            chunk_data = []
            for i, chunk_text in enumerate(chunks):
                chunk_data.append({
                    'text': chunk_text,
                    'chunk_index': i,
                    'metadata': {
                        'category': primary_cat,
                        'subcategory': subcategory,
                        'difficulty': chapter_info.get("difficulty", 3),
                        'source': book_info["title"],
                        'source_book': book_info["short_name"],
                        'tags': book_info.get("secondary_categories", [])
                    }
                })

            # Upload to Pinecone
            vector_ids = vector_store.upsert_chunks(
                chunks=chunk_data,
                node_id=node.id,
                node_metadata={
                    'title': title,
                    'category': primary_cat,
                    'subcategory': subcategory,
                    'source_book': book_info["short_name"],
                    'tags': book_info.get("secondary_categories", [])
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
            print(f"    ✅ Indexed {len(chunks)} chunks")

            extractor.close()
            self.indexed_count += 1
            return node.id

        except Exception as e:
            print(f"  ❌ Error indexing chapter: {e}")
            import traceback
            traceback.print_exc()
            self.error_count += 1
            return None

    def index_book(self, pdf_path: Path, book_info: Dict):
        """Index all chapters from a book"""
        print(f"\n📖 Indexing: {book_info['title']}")
        print(f"   Primary category: {book_info['primary_category']}")
        print(f"   Tags: {', '.join(book_info.get('secondary_categories', []))}")
        print(f"   Chapters to index: {len(book_info.get('chapters', []))}")

        chapters = book_info.get("chapters", [])

        if not chapters:
            print(f"  ⚠️  No chapters defined in BOOK_REGISTRY. Add chapter definitions to index this book.")
            return

        for chapter_info in chapters:
            self.index_book_chapter(book_info, chapter_info, pdf_path)

    def index_new_books(self, content_dir: str = "../content"):
        """Index only books that haven't been indexed yet"""
        print("\n🚀 Starting indexing of NEW books...")

        report = self.scan_books(content_dir)

        if not report["ready_to_index"]:
            print("\n✅ All books already indexed! Nothing to do.")
            return

        print(f"\n📚 Indexing {len(report['ready_to_index'])} new book(s)...")

        pdfs = self.find_all_pdfs(content_dir)

        for pdf_path in pdfs:
            book_info = self.get_book_info(pdf_path)

            if not book_info:
                continue

            # Check if already indexed
            if self.is_book_indexed(book_info["short_name"]):
                continue

            # Index this book
            self.index_book(pdf_path, book_info)

        self.print_summary()

    def index_specific_book(self, filename: str, content_dir: str = "../content"):
        """Index a specific book by filename"""
        pdfs = self.find_all_pdfs(content_dir)

        target_pdf = None
        for pdf_path in pdfs:
            if pdf_path.name == filename:
                target_pdf = pdf_path
                break

        if not target_pdf:
            print(f"❌ PDF '{filename}' not found in {content_dir}")
            return

        book_info = self.get_book_info(target_pdf)

        if not book_info:
            print(f"❌ '{filename}' is not registered in BOOK_REGISTRY")
            print(f"   Add it to BOOK_REGISTRY in this script to enable indexing")
            return

        self.index_book(target_pdf, book_info)
        self.print_summary()

    def print_summary(self):
        """Print indexing summary"""
        print("\n" + "=" * 80)
        print("📊 INDEXING SUMMARY")
        print("=" * 80)
        print(f"  ✅ Successfully indexed: {self.indexed_count} chapters")
        print(f"  ⏭️  Skipped (already exist): {self.skipped_count} chapters")
        print(f"  ❌ Errors: {self.error_count} chapters")
        print("=" * 80)

    def _get_category_color(self, category: str) -> str:
        """Get color for category"""
        colors = {
            "linear_algebra": "#3b82f6",
            "calculus": "#10b981",
            "probability": "#f59e0b",
            "statistics": "#8b5cf6",
            "machine_learning": "#ec4899",
            "finance": "#14b8a6",  # NEW: Teal for finance
            "deep_learning": "#6366f1",
        }
        return colors.get(category, "#6b7280")

    def _get_category_icon(self, category: str) -> str:
        """Get icon for category"""
        icons = {
            "linear_algebra": "🔷",
            "calculus": "∫",
            "probability": "🎲",
            "statistics": "📊",
            "machine_learning": "🤖",
            "finance": "💹",  # NEW: Finance icon
            "deep_learning": "🧠",
        }
        return icons.get(category, "📚")

    def close(self):
        """Close database connection"""
        self.db.close()


# ==================== CLI ====================

def main():
    parser = argparse.ArgumentParser(
        description="Universal Book Indexer - Smart indexing with multi-category support",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --scan                                  # Scan and report status
  %(prog)s --index-new                             # Index new books only
  %(prog)s --book "advances_in_financial_ml.pdf"   # Index specific book
  %(prog)s --init-db --index-new                   # Initialize DB first, then index
        """
    )

    parser.add_argument('--scan', action='store_true',
                        help='Scan PDFs and show indexing status')
    parser.add_argument('--index-new', action='store_true',
                        help='Index books that have not been indexed yet')
    parser.add_argument('--book', type=str,
                        help='Index a specific book by filename')
    parser.add_argument('--content-dir', default='../content',
                        help='Content directory (default: ../content)')
    parser.add_argument('--init-db', action='store_true',
                        help='Initialize database before indexing')

    args = parser.parse_args()

    # Initialize database if requested
    if args.init_db:
        print("Initializing database...")
        init_db()

    indexer = UniversalBookIndexer()

    try:
        if args.scan:
            # Scan mode
            report = indexer.scan_books(args.content_dir)
            indexer.print_scan_report(report)

        elif args.index_new:
            # Index new books
            indexer.index_new_books(args.content_dir)

        elif args.book:
            # Index specific book
            indexer.index_specific_book(args.book, args.content_dir)

        else:
            # No action specified - show scan by default
            report = indexer.scan_books(args.content_dir)
            indexer.print_scan_report(report)
            print("\nℹ️  Use --index-new to index books that are ready")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        indexer.close()


if __name__ == "__main__":
    main()
