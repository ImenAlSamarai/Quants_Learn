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

    # Extract text from all pages
    print("\n📝 Extracting text...")
    full_text = []
    for page_num in range(total_pages):
        page = doc[page_num]
        text = page.get_text()
        full_text.append(text)

        if (page_num + 1) % 50 == 0:
            print(f"   Processed {page_num + 1}/{total_pages} pages...")

    doc.close()
    print(f"   ✅ Extracted text from {total_pages} pages")

    # Combine and clean text
    combined_text = "\n\n".join(full_text)
    print(f"   Total characters: {len(combined_text):,}")

    # Chunk the text
    print("\n🔪 Chunking text...")
    chunks = chunk_text(combined_text, chunk_size=1500, overlap=300)
    print(f"   Created {len(chunks)} chunks")

    # Index chunks into Pinecone
    print(f"\n💾 Indexing into Pinecone...")
    indexed_count = 0
    batch_size = 100  # Process in batches to avoid memory issues

    for i in range(0, len(chunks), batch_size):
        batch_chunks = chunks[i:i + batch_size]
        batch_texts = []
        batch_metadata = []

        for idx, chunk in enumerate(batch_chunks):
            chunk_num = i + idx

            # Prepare metadata
            metadata = {
                'source': book_name,
                'subject': subject,
                'chunk_id': chunk_num,
                'total_chunks': len(chunks),
                'text': chunk  # Store actual text in metadata for retrieval
            }

            batch_texts.append(chunk)
            batch_metadata.append(metadata)

        # Upsert batch to Pinecone
        try:
            vector_store.upsert_chunks(batch_texts, batch_metadata)
            indexed_count += len(batch_chunks)
            print(f"   Indexed {indexed_count}/{len(chunks)} chunks...")
            time.sleep(0.5)  # Rate limiting
        except Exception as e:
            print(f"   ⚠️  Error indexing batch {i//batch_size + 1}: {e}")
            continue

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
