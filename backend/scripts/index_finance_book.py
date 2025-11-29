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

        # Chunk this batch
        batch_chunks = chunk_text(combined_batch_text, chunk_size=1500, overlap=300)
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
