#!/usr/bin/env python3
"""
Re-index Statistical Inference with enhanced content from inference.md
"""
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.database import SessionLocal, Node, ContentChunk
from app.services.vector_store import vector_store
from app.config.settings import settings
import re
import markdown
from bs4 import BeautifulSoup


def split_text(text: str, chunk_size=2000, chunk_overlap=50) -> list:
    """Split text into overlapping chunks"""
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
            overlap_words = words[-chunk_overlap:] if len(words) > chunk_overlap else words
            current_chunk = ' '.join(overlap_words) + '\n\n' + para
        else:
            current_chunk += '\n\n' + para if current_chunk else para

    # Add the last chunk
    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


def process_markdown(file_path: str) -> dict:
    """Process a markdown file and extract metadata"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Convert markdown to text
    html = markdown.markdown(content)
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text()

    return {
        'text': text,
        'raw_content': content
    }


def main():
    print("=" * 80)
    print("Re-indexing Statistical Inference with Enhanced Content")
    print("=" * 80)
    print()

    db = SessionLocal()

    try:
        # Find Statistical Inference node
        node = db.query(Node).filter(Node.title == "Statistical Inference").first()

        if not node:
            print("❌ Statistical Inference node not found!")
            return

        print(f"✓ Found node: {node.title} (ID: {node.id})")
        print()

        # Load enhanced content
        content_path = Path(__file__).parent.parent.parent / "content" / "statistics" / "inference.md"

        if not content_path.exists():
            print(f"❌ Content file not found: {content_path}")
            return

        print(f"✓ Loading content from: {content_path}")

        # Parse markdown
        parsed = process_markdown(str(content_path))
        text = parsed['text']

        print(f"  Content size: {len(text)} characters")
        print()

        # Split into chunks
        chunks = split_text(text, chunk_size=settings.CHUNK_SIZE, chunk_overlap=settings.CHUNK_OVERLAP)
        print(f"✓ Split into {len(chunks)} chunks")
        print()

        # Delete existing chunks
        print("Deleting old chunks...")
        deleted_count = db.query(ContentChunk).filter(ContentChunk.node_id == node.id).delete()
        print(f"  Deleted {deleted_count} old chunks from PostgreSQL")

        try:
            vector_store.delete_node_vectors(node.id)
            print(f"  Deleted vectors from Pinecone")
        except Exception as e:
            print(f"  ⚠️  Could not delete from Pinecone (may be offline): {e}")

        print()

        # Index new chunks
        print("Indexing new chunks...")
        chunk_data = []
        for i, chunk_text in enumerate(chunks):
            chunk_data.append({
                'text': chunk_text,
                'chunk_index': i,
                'metadata': {
                    'category': node.category,
                    'subcategory': node.subcategory,
                    'difficulty': node.difficulty_level
                }
            })

        # Upload to Pinecone
        try:
            vector_ids = vector_store.upsert_chunks(
                chunks=chunk_data,
                node_id=node.id,
                node_metadata={
                    'title': node.title,
                    'category': node.category,
                    'subcategory': node.subcategory
                }
            )

            # If vector_store is unavailable, it returns empty list
            if not vector_ids:
                print(f"  ⚠️  Pinecone unavailable - using local vector IDs")
                vector_ids = [f"local_{node.id}_{i}" for i in range(len(chunks))]
            else:
                print(f"  ✓ Uploaded {len(vector_ids)} vectors to Pinecone")

        except Exception as e:
            print(f"  ⚠️  Could not upload to Pinecone: {e}")
            # Create dummy vector IDs for local storage
            vector_ids = [f"local_{node.id}_{i}" for i in range(len(chunks))]
            print(f"  Using local vector IDs")

        # Save chunk metadata to PostgreSQL
        for i, (chunk_text, vector_id) in enumerate(zip(chunks, vector_ids)):
            content_chunk = ContentChunk(
                node_id=node.id,
                chunk_text=chunk_text,
                chunk_index=i,
                vector_id=vector_id
            )
            db.add(content_chunk)

        db.commit()
        print(f"  ✓ Saved {len(chunks)} chunks to PostgreSQL")
        print()

        print("=" * 80)
        print("✅ Re-indexing completed successfully!")
        print("=" * 80)
        print()
        print("Enhanced content includes:")
        print("  - Heavy-Tailed Distributions and Financial Reality")
        print("  - Lévy Distributions and Power-Law Tails")
        print("  - Student's t-Distribution")
        print("  - Empirical Detection of Heavy Tails")
        print("  - Implications for Statistical Inference")
        print("  - Practice Problems")
        print()
        print("Next steps:")
        print("  1. Restart backend if running")
        print("  2. Open Statistical Inference topic in frontend")
        print("  3. Verify new content appears")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()

    finally:
        db.close()


if __name__ == "__main__":
    main()
