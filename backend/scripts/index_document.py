"""
Universal PDF Document Indexer with Optimized Sliding Window Chunking

Indexes any PDF book into Pinecone using token-based sliding window approach.
- 256 tokens per chunk (industry standard for RAG)
- 128 token overlap (50% - prevents context loss at boundaries)
- Better semantic coherence and retrieval accuracy

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
import tiktoken
from app.services.vector_store import vector_store
from app.config.settings import settings
import time


def chunk_text_sliding_window(text, chunk_size=256, overlap=128, encoding_name="cl100k_base"):
    """
    Split text into overlapping chunks using sliding window approach with tiktoken.

    This is the industry-standard approach for RAG systems:
    - Token-based (not character-based) for accurate chunk sizes
    - Sliding window with 50% overlap prevents context loss
    - Smaller chunks (256 tokens) improve retrieval precision

    Args:
        text: Full text to chunk
        chunk_size: Target size of each chunk in tokens (default: 256)
        overlap: Number of tokens to overlap between chunks (default: 128)
        encoding_name: tiktoken encoding to use (default: cl100k_base)

    Returns:
        List of text chunks
    """
    # Initialize tiktoken encoder
    encoding = tiktoken.get_encoding(encoding_name)

    # Encode text to tokens
    tokens = encoding.encode(text)

    chunks = []
    start = 0

    while start < len(tokens):
        # Get chunk of tokens
        end = min(start + chunk_size, len(tokens))
        chunk_tokens = tokens[start:end]

        # Decode back to text
        chunk_text = encoding.decode(chunk_tokens)
        chunks.append(chunk_text)

        # Move start position (with overlap)
        # If chunk_size=256 and overlap=128, next chunk starts at position 128
        start += (chunk_size - overlap)

        # Stop if we've reached the end
        if end >= len(tokens):
            break

    return chunks


def index_pdf(pdf_path, book_name, subjects="finance", namespace=""):
    """
    Index a PDF book into Pinecone using optimized chunking strategy.

    Args:
        pdf_path: Path to PDF file
        book_name: Name of the book for metadata
        subjects: Subject categories - comma-separated string or list
                 (e.g., "machine_learning,statistics,finance" or ["ml", "stats"])
        namespace: Pinecone namespace (default: "" for main namespace)
    """
    # Parse subjects into list
    if isinstance(subjects, str):
        subject_list = [s.strip() for s in subjects.split(',')]
    else:
        subject_list = subjects

    # Primary subject for vector ID (first in list)
    primary_subject = subject_list[0]

    print(f"\n{'='*80}")
    print(f"📚 Indexing: {book_name}")
    print(f"📄 Path: {pdf_path}")
    print(f"🏷️  Subjects: {', '.join(subject_list)}")
    print(f"📊 Chunking: {settings.CHUNK_SIZE} tokens, {settings.CHUNK_OVERLAP} overlap")
    print(f"{'='*80}\n")

    # Check if file exists
    if not os.path.exists(pdf_path):
        print(f"❌ ERROR: File not found: {pdf_path}")
        print(f"\nCurrent working directory: {os.getcwd()}")
        print(f"Absolute path attempted: {os.path.abspath(pdf_path)}")
        print(f"\nMake sure the file exists and the path is correct.")
        return

    # Open PDF
    print("📖 Opening PDF...")
    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    print(f"   Total pages: {total_pages}\n")

    # Extract all text first (more efficient for token-based chunking)
    print("📝 Extracting text from all pages...")
    all_text = []
    for page_num in range(total_pages):
        page = doc[page_num]
        text = page.get_text()
        all_text.append(text)

        if (page_num + 1) % 50 == 0:
            print(f"   Extracted {page_num + 1}/{total_pages} pages...")

    doc.close()

    # Combine all text
    full_text = "\n\n".join(all_text)
    print(f"   ✅ Extracted {len(full_text):,} characters from {total_pages} pages\n")

    # Chunk using sliding window approach
    print(f"✂️  Chunking text ({settings.CHUNK_SIZE} tokens, {settings.CHUNK_OVERLAP} overlap)...")
    chunks = chunk_text_sliding_window(
        full_text,
        chunk_size=settings.CHUNK_SIZE,
        overlap=settings.CHUNK_OVERLAP,
        encoding_name=settings.TOKENIZER_MODEL
    )
    print(f"   ✅ Created {len(chunks)} chunks\n")

    # Index chunks to Pinecone
    print(f"🚀 Indexing {len(chunks)} chunks to Pinecone...")
    indexed_count = 0
    failed_count = 0

    # Process in batches to avoid memory issues
    batch_size = 100
    for batch_start in range(0, len(chunks), batch_size):
        batch_end = min(batch_start + batch_size, len(chunks))
        batch_chunks = chunks[batch_start:batch_end]

        vectors = []
        for i, chunk in enumerate(batch_chunks):
            chunk_id = batch_start + i
            try:
                # Generate embedding
                embedding = vector_store.generate_embedding(chunk)

                # Create vector ID (use primary subject)
                vector_id = f"{primary_subject}_{book_name.replace(' ', '_').replace('-', '_')}_{chunk_id}"

                # Prepare metadata with multi-subject tagging
                metadata = {
                    'source': book_name,
                    'subjects': subject_list,  # Multiple subjects as list
                    'primary_subject': primary_subject,  # First subject
                    'chunk_id': chunk_id,
                    'text': chunk[:1000],  # Store first 1000 chars for display
                    'content_type': 'pdf_book'
                }

                vectors.append({
                    'id': vector_id,
                    'values': embedding,
                    'metadata': metadata
                })

            except Exception as e:
                print(f"   ⚠️  Error processing chunk {chunk_id}: {e}")
                failed_count += 1

        # Upsert batch to Pinecone
        if vectors:
            try:
                vector_store.index.upsert(vectors=vectors, namespace=namespace)
                indexed_count += len(vectors)
                print(f"   ✅ Indexed {indexed_count}/{len(chunks)} chunks...", end='\r')
            except Exception as e:
                print(f"\n   ❌ Error upserting batch {batch_start}-{batch_end}: {e}")
                failed_count += len(vectors)

    print(f"\n\n✅ Successfully indexed {indexed_count} chunks from '{book_name}'")
    if failed_count > 0:
        print(f"⚠️  {failed_count} chunks failed to index")
    print(f"{'='*80}\n")

    return {
        'book_name': book_name,
        'total_pages': total_pages,
        'total_chunks': len(chunks),
        'indexed_chunks': indexed_count,
        'failed_chunks': failed_count
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Universal PDF Document Indexer with Optimized Chunking",
        epilog="Example: python scripts/index_document.py ../content/trading/Python_for_Algo.pdf"
    )
    parser.add_argument(
        'pdf_path',
        type=str,
        help='Path to PDF file (e.g., ../content/finance/book.pdf)'
    )
    parser.add_argument(
        '--subjects',
        type=str,
        help='Subject categories (comma-separated, e.g., "machine_learning,statistics,finance")'
    )
    parser.add_argument(
        '--namespace',
        type=str,
        default='',
        help='Pinecone namespace for organizing content (default: "" for main)'
    )

    args = parser.parse_args()
    pdf_path = args.pdf_path

    # Auto-detect book name from filename
    filename = Path(pdf_path).stem
    book_name = filename.replace('_', ' ').replace('  ', ' ').strip()

    # Get subjects (use provided or default to 'general')
    if args.subjects:
        subjects = args.subjects
    else:
        subjects = 'general'

    print(f"\n{'='*80}")
    print(f"🚀 Universal PDF Book Indexer (Multi-Subject)")
    print(f"{'='*80}")
    print(f"📄 PDF Path: {pdf_path}")
    print(f"📚 Book Name: {book_name} (auto-detected)")
    print(f"🏷️  Subjects: {subjects}")
    print(f"📊 Strategy: Sliding window ({settings.CHUNK_SIZE} tokens, {settings.CHUNK_OVERLAP} overlap)")
    print(f"{'='*80}\n")

    # Index the book
    result = index_pdf(
        pdf_path=pdf_path,
        book_name=book_name,
        subjects=subjects,
        namespace=args.namespace
    )

    print("\n🎉 Indexing complete!")
    print(f"\n📊 Summary:")
    print(f"   Pages: {result['total_pages']}")
    print(f"   Chunks created: {result['total_chunks']}")
    print(f"   Chunks indexed: {result['indexed_chunks']}")
    if result['failed_chunks'] > 0:
        print(f"   Failed: {result['failed_chunks']}")

    print("\n📝 Next steps:")
    print("1. Submit a job description with topics covered by this book")
    print("2. The system should detect coverage from indexed content")
    print("3. Learning content can be generated using these chunks\n")
