"""
Simple PDF Indexer for Finance Books
Indexes "Advances in Financial Machine Learning" into Pinecone
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import fitz  # PyMuPDF
from app.services.vector_store import vector_store
import time

def chunk_text(text, chunk_size=1000, overlap=200):
    """
    Split text into overlapping chunks

    Args:
        text: Full text to chunk
        chunk_size: Target size of each chunk in characters
        overlap: Number of characters to overlap between chunks

    Returns:
        List of text chunks
    """
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        # Try to end at a sentence boundary
        if end < len(text):
            # Find last period, exclamation, or question mark
            last_period = max(
                chunk.rfind('.'),
                chunk.rfind('!'),
                chunk.rfind('?'),
                chunk.rfind('\n\n')
            )
            if last_period > chunk_size * 0.5:  # Don't make chunks too small
                chunk = chunk[:last_period + 1]

        chunks.append(chunk.strip())
        start = start + len(chunk) - overlap

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
    page_batch_size = 50  # Process 50 pages at a time
    all_chunks = []
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

        # Chunk this batch
        batch_chunks = chunk_text(combined_batch_text, chunk_size=1500, overlap=300)
        print(f"      Created {len(batch_chunks)} chunks")

        # Index chunks from this batch immediately
        upload_batch_size = 50  # Upload 50 chunks at a time
        for i in range(0, len(batch_chunks), upload_batch_size):
            upload_chunks = batch_chunks[i:i + upload_batch_size]
            batch_texts = []
            batch_metadata = []

            for chunk in upload_chunks:
                # Prepare metadata
                metadata = {
                    'source': book_name,
                    'subject': subject,
                    'chunk_id': total_chunk_count,
                    'text': chunk  # Store actual text in metadata for retrieval
                }
                total_chunk_count += 1

                batch_texts.append(chunk)
                batch_metadata.append(metadata)

            # Upsert batch to Pinecone
            try:
                vector_store.upsert_chunks(batch_texts, batch_metadata)
                indexed_count += len(upload_chunks)
                print(f"      ✅ Indexed {indexed_count} chunks so far...")
                time.sleep(0.5)  # Rate limiting
            except Exception as e:
                print(f"      ⚠️  Error indexing: {e}")
                continue

        # Clear memory
        del batch_text
        del combined_batch_text
        del batch_chunks

    doc.close()
    print(f"\n✅ Successfully indexed {indexed_count} chunks from '{book_name}'")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    # Path to your PDF (relative to backend directory)
    pdf_path = "../content/finance/Advances_in_Financial_Machine_Learning.pdf"

    # Index the book
    index_pdf(
        pdf_path=pdf_path,
        book_name="Advances in Financial Machine Learning",
        subject="finance"
    )

    print("\n🎉 Indexing complete!")
    print("\nNext steps:")
    print("1. Submit a job description with 'alpha generation' or 'machine learning for finance'")
    print("2. The system should now detect coverage from this book")
    print("3. Learning content can be generated using these chunks\n")
