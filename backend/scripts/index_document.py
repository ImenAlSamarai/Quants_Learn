"""
Universal PDF Document Indexer

Indexes any PDF book into Pinecone for semantic search and RAG.
Auto-detects book name from filename and subject from directory.

Usage:
    python scripts/index_document.py <path_to_pdf>
    python scripts/index_document.py ../content/trading/book.pdf --subject trading
"""

import sys
import os
import re
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import fitz  # PyMuPDF
from app.services.vector_store import vector_store
import time

def chunk_text(text, chunk_size=1000, overlap=50):
    """
    Split text into overlapping chunks (paragraph-based, proven algorithm)

    Args:
        text: Full text to chunk
        chunk_size: Target size of each chunk in characters
        overlap: Number of words to overlap between chunks

    Returns:
        List of text chunks
    """
    # Remove multiple newlines and extra spaces
    text = re.sub(r'\n\s*\n', '\n\n', text)

    # Split by paragraphs first
    paragraphs = text.split('\n\n')

    chunks = []
    current_chunk = ""

    for para in paragraphs:
        # If adding this paragraph exceeds chunk size, save current chunk
        if len(current_chunk) + len(para) > chunk_size and current_chunk:
            chunks.append(current_chunk.strip())

            # Start new chunk with overlap (last few words of previous chunk)
            words = current_chunk.split()
            overlap_words = words[-overlap:] if len(words) > overlap else words
            current_chunk = ' '.join(overlap_words) + '\n\n' + para
        else:
            current_chunk += '\n\n' + para if current_chunk else para

    # Add the last chunk
    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


def index_pdf(pdf_path, book_name, subject="finance"):
    """
    Index a PDF book into Pinecone

    Args:
        pdf_path: Path to PDF file
        book_name: Name of the book for metadata
        subject: Subject category (e.g., "finance", "statistics")
    """
    print(f"\n{'='*80}")
    print(f"Indexing: {book_name}")
    print(f"Path: {pdf_path}")
    print(f"{'='*80}\n")

    # Check if file exists
    if not os.path.exists(pdf_path):
        print(f"❌ ERROR: File not found: {pdf_path}")
        print(f"\nExpected location (relative to backend/):")
        print(f"  ../content/finance/Advances_in_Financial_Machine_Learning.pdf")
        return

    # Open PDF
    print("📖 Opening PDF...")
    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    print(f"   Total pages: {total_pages}")

    # Process in page batches to avoid memory issues
    print("\n📝 Processing PDF in batches...")
    page_batch_size = 25  # Process 25 pages at a time (smaller batches)
    total_chunk_count = 0
    indexed_count = 0

    for batch_start in range(0, total_pages, page_batch_size):
        batch_end = min(batch_start + page_batch_size, total_pages)
        print(f"\n   📄 Processing pages {batch_start + 1}-{batch_end}/{total_pages}...")

        # Extract text from this batch of pages
        batch_text = []
        for page_num in range(batch_start, batch_end):
            page = doc[page_num]
            text = page.get_text()
            batch_text.append(text)

        # Combine batch text
        combined_batch_text = "\n\n".join(batch_text)
        print(f"      Extracted {len(combined_batch_text):,} characters")

        # Chunk this batch (overlap is in words, not characters)
        batch_chunks = chunk_text(combined_batch_text, chunk_size=1000, overlap=50)
        print(f"      Created {len(batch_chunks)} chunks")

        # Process chunks one at a time to minimize memory usage
        print(f"      Indexing chunks...")
        for chunk in batch_chunks:
            try:
                # Generate embedding for this single chunk
                embedding = vector_store.generate_embedding(chunk)

                # Create vector ID
                vector_id = f"finance_{book_name.replace(' ', '_')}_{total_chunk_count}"

                # Prepare metadata
                metadata = {
                    'source': book_name,
                    'subject': subject,
                    'chunk_id': total_chunk_count,
                    'text': chunk[:1000]  # Store truncated text
                }

                # Upsert single vector to Pinecone
                vector_store.index.upsert(vectors=[{
                    'id': vector_id,
                    'values': embedding,
                    'metadata': metadata
                }])

                total_chunk_count += 1
                indexed_count += 1

                # Progress indicator every 10 chunks
                if indexed_count % 10 == 0:
                    print(f"      ✅ Indexed {indexed_count} chunks...", end='\r')

            except Exception as e:
                print(f"\n      ⚠️  Error indexing chunk {total_chunk_count}: {e}")
                total_chunk_count += 1
                continue

        # Clear memory after each page batch
        del batch_text
        del combined_batch_text
        del batch_chunks

        print(f"      ✅ Batch complete: {indexed_count} total chunks indexed")

    doc.close()
    print(f"\n✅ Successfully indexed {indexed_count} chunks from '{book_name}'")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Universal PDF Document Indexer - Just point it at any PDF!",
        epilog="Example: python scripts/index_document.py ../content/trading/Python_for_Algo.pdf"
    )
    parser.add_argument(
        'pdf_path',
        type=str,
        help='Path to PDF file (e.g., ../content/finance/book.pdf)'
    )
    parser.add_argument(
        '--subject',
        type=str,
        help='Override subject category (default: auto-detect from folder name)'
    )

    args = parser.parse_args()
    pdf_path = args.pdf_path

    # Auto-detect book name from filename
    # "Python_for_Algorithmic_Trading_ From Idea.pdf" -> "Python for Algorithmic Trading From Idea"
    filename = Path(pdf_path).stem
    book_name = filename.replace('_', ' ').replace('  ', ' ').strip()

    # Auto-detect subject from parent directory name
    # "../content/trading/book.pdf" -> "trading"
    # "../content/finance/book.pdf" -> "finance"
    if args.subject:
        subject = args.subject
    else:
        parent_dir = Path(pdf_path).parent.name
        subject = parent_dir if parent_dir not in ['content', '.', '..'] else 'general'

    print(f"\n{'='*80}")
    print(f"Universal PDF Book Indexer")
    print(f"{'='*80}")
    print(f"PDF Path: {pdf_path}")
    print(f"Book Name: {book_name} (auto-detected)")
    print(f"Subject: {subject} (auto-detected)")
    print(f"{'='*80}\n")

    # Index the book
    index_pdf(
        pdf_path=pdf_path,
        book_name=book_name,
        subject=subject
    )

    print("\n🎉 Indexing complete!")
    print("\nNext steps:")
    print("1. Submit a job description with topics covered by this book")
    print("2. The system should detect coverage from indexed content")
    print("3. Learning content can be generated using these chunks\n")

