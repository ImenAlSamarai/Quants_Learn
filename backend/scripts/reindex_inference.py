#!/usr/bin/env python3
"""
Reindex Statistics Inference Content

This script reindexes the Statistical Inference topic with updated content.
Useful when inference.md has been updated (e.g., with Bouchaud Ch1 enhancements).

Usage:
    python scripts/reindex_inference.py
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.database import SessionLocal, Node, ContentChunk
from app.services.vector_store import vector_store
from scripts.index_content import ContentIndexer


def main():
    print("=" * 80)
    print("Reindexing Statistical Inference with Enhanced Content")
    print("=" * 80)
    print()

    db = SessionLocal()
    indexer = ContentIndexer()

    try:
        # Find the inference node
        node = db.query(Node).filter(
            Node.title == 'Statistical Inference',
            Node.category == 'statistics'
        ).first()

        if not node:
            print("❌ Error: Statistical Inference node not found in database")
            print("Run index_content.py first to create the node structure")
            return 1

        print(f"✓ Found node: {node.title} (ID: {node.id})")
        print(f"  Current content path: {node.content_path}")
        print()

        # Check if content file exists
        content_path = Path(node.content_path)
        if not content_path.exists():
            print(f"❌ Error: Content file not found: {content_path}")
            print()
            print("Expected file locations:")
            print("  • content/statistics/inference.md")
            print("  • content/statistics/inference_enhanced.md")
            return 1

        print(f"✓ Content file exists: {content_path}")
        file_size_kb = content_path.stat().st_size / 1024
        print(f"  File size: {file_size_kb:.1f} KB")
        print()

        # Show current chunks
        current_chunks = db.query(ContentChunk).filter(
            ContentChunk.node_id == node.id
        ).count()
        print(f"Current state: {current_chunks} chunks indexed")
        print()

        # Ask for confirmation
        response = input("Proceed with reindexing? This will delete old chunks and create new ones. (y/n): ")
        if response.lower() != 'y':
            print("Cancelled.")
            return 0

        print()
        print("=" * 80)
        print("Starting Reindex Process")
        print("=" * 80)
        print()

        # Delete old chunks
        print(f"1. Deleting {current_chunks} old chunks from database...")
        old_chunks = db.query(ContentChunk).filter(ContentChunk.node_id == node.id).all()

        # Delete from Pinecone
        vector_ids_to_delete = [chunk.vector_id for chunk in old_chunks if chunk.vector_id]
        if vector_ids_to_delete:
            print(f"   Deleting {len(vector_ids_to_delete)} vectors from Pinecone...")
            vector_store.delete_vectors(vector_ids_to_delete)

        # Delete from database
        db.query(ContentChunk).filter(ContentChunk.node_id == node.id).delete()
        db.commit()
        print("   ✓ Old chunks deleted")
        print()

        # Process new content
        print("2. Processing content...")
        parsed = indexer.process_markdown(str(content_path))
        text = parsed['text']
        print(f"   Read {len(text)} characters")

        # Split into chunks
        print("3. Creating chunks...")
        chunks = indexer.split_text(text)
        print(f"   ✓ Split into {len(chunks)} chunks")
        print()

        # Check for Bouchaud content
        bouchaud_found = any('bouchaud' in chunk.lower() or 'lévy' in chunk.lower() or 'heavy-tail' in chunk.lower() for chunk in chunks)
        if bouchaud_found:
            print("   ✓ Bouchaud content detected in chunks!")
        else:
            print("   ⚠️  Warning: No Bouchaud content found. Are you using inference_enhanced.md?")
        print()

        # Index chunks
        print("4. Indexing chunks to Pinecone...")
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

        # Upload to Pinecone with embeddings
        vector_ids = vector_store.upsert_chunks(
            chunks=chunk_data,
            node_id=node.id,
            node_metadata={
                'title': node.title,
                'category': node.category
            }
        )
        print(f"   ✓ Uploaded {len(vector_ids)} vectors to Pinecone")
        print()

        # Save chunk references to database
        print("5. Saving chunk metadata to database...")
        for i, (chunk_text, vector_id) in enumerate(zip(chunks, vector_ids)):
            chunk = ContentChunk(
                node_id=node.id,
                chunk_text=chunk_text,
                chunk_index=i,
                vector_id=vector_id
            )
            db.add(chunk)

        db.commit()
        print(f"   ✓ Saved {len(chunks)} chunk records")
        print()

        # Verify
        print("=" * 80)
        print("Verification")
        print("=" * 80)
        print()

        new_chunk_count = db.query(ContentChunk).filter(
            ContentChunk.node_id == node.id
        ).count()

        bouchaud_chunks = db.query(ContentChunk).filter(
            ContentChunk.node_id == node.id,
            ContentChunk.chunk_text.ilike('%bouchaud%')
        ).count()

        heavy_tail_chunks = db.query(ContentChunk).filter(
            ContentChunk.node_id == node.id,
            ContentChunk.chunk_text.ilike('%heavy%tail%')
        ).count()

        levy_chunks = db.query(ContentChunk).filter(
            ContentChunk.node_id == node.id,
            ContentChunk.chunk_text.ilike('%lévy%')
        ).count()

        print(f"Total chunks: {new_chunk_count}")
        print(f"Chunks mentioning 'Bouchaud': {bouchaud_chunks}")
        print(f"Chunks mentioning 'heavy-tailed': {heavy_tail_chunks}")
        print(f"Chunks mentioning 'Lévy': {levy_chunks}")
        print()

        if bouchaud_chunks > 0 or heavy_tail_chunks > 0 or levy_chunks > 0:
            print("✅ SUCCESS! Bouchaud content is now indexed!")
            print()
            print("Next steps:")
            print("  1. Test RAG retrieval: python scripts/test_bouchaud_retrieval.py")
            print("  2. Check frontend: Navigate to Statistical Inference topic")
            print("  3. Query: 'What are heavy-tailed distributions?'")
        else:
            print("⚠️  WARNING: No Bouchaud content found in indexed chunks")
            print()
            print("Troubleshooting:")
            print(f"  1. Check file content: cat {content_path}")
            print("  2. Ensure you're using inference_enhanced.md (15KB), not inference.md (6.8KB)")
            print("  3. File should contain 'Bouchaud', 'Lévy', 'heavy-tailed distributions'")

        return 0

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
