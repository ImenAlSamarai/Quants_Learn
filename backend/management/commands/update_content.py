"""
Update Content Command

Handles content reindexing + automatic cache invalidation.
Replaces: reindex_inference.py and manual cache clearing.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.models.database import SessionLocal, Node, ContentChunk, GeneratedContent
from app.services.vector_store import VectorStoreService
from app.services.content_indexer import ContentIndexer
from datetime import datetime


class UpdateContentCommand:
    """Update and reindex node content"""

    def __init__(self):
        self.db = None

    def run(self, node_id, verify=False):
        """
        Update content for a node

        Steps:
        1. Get node
        2. Delete old chunks (DB + Pinecone)
        3. Reindex content
        4. Increment content_version (auto-invalidates cache)
        5. Verify (optional)
        """
        self.db = SessionLocal()

        try:
            print("=" * 80)
            print(f" UPDATE CONTENT: Node {node_id}")
            print("=" * 80)
            print()

            # Step 1: Get node
            node = self.db.query(Node).filter(Node.id == node_id).first()
            if not node:
                print(f"❌ Node {node_id} not found")
                return 1

            print(f"Node: {node.title}")
            print(f"Category: {node.category}")
            print(f"Content: {node.content_path}")
            print()

            # Step 2: Delete old chunks
            print("Step 1: Deleting old chunks...")
            self._delete_old_chunks(node)

            # Step 3: Reindex content
            print("\nStep 2: Reindexing content...")
            self._reindex_content(node)

            # Step 4: Increment version (auto-invalidates cache)
            print("\nStep 3: Incrementing content version...")
            self._increment_version(node)

            # Step 5: Verify
            if verify:
                print("\nStep 4: Verifying...")
                self._verify_content(node)

            print("\n" + "=" * 80)
            print("✅ Content updated successfully")
            print("=" * 80)
            print()
            print("Cache automatically invalidated - new content will generate on next request")

            return 0

        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return 1

        finally:
            if self.db:
                self.db.close()

    def _delete_old_chunks(self, node):
        """Delete old chunks from DB and Pinecone"""
        # Delete from Pinecone
        vector_store = VectorStoreService()
        if vector_store.available:
            vector_store.delete_node_vectors(node.id)
            print(f"  ✓ Deleted vectors from Pinecone")

        # Delete from database
        chunk_count = self.db.query(ContentChunk).filter(
            ContentChunk.node_id == node.id
        ).count()

        self.db.query(ContentChunk).filter(
            ContentChunk.node_id == node.id
        ).delete()
        self.db.commit()

        print(f"  ✓ Deleted {chunk_count} chunks from database")

    def _reindex_content(self, node):
        """Reindex content from markdown file"""
        from app.services.content_indexer import ContentIndexer

        indexer = ContentIndexer()

        # Read and parse markdown
        try:
            chunks = indexer.index_node_content(
                node_id=node.id,
                markdown_path=node.content_path
            )

            print(f"  ✓ Indexed {len(chunks)} new chunks")

        except Exception as e:
            print(f"  ❌ Reindexing failed: {e}")
            raise

    def _increment_version(self, node):
        """Increment content version (invalidates cache automatically)"""
        # Add content_version if it doesn't exist
        if not hasattr(node, 'content_version') or node.content_version is None:
            # Check if column exists in extra_metadata
            if node.extra_metadata is None:
                node.extra_metadata = {}
            node.extra_metadata['content_version'] = 1
        else:
            # Increment version
            if isinstance(node.extra_metadata, dict):
                current = node.extra_metadata.get('content_version', 0)
                node.extra_metadata['content_version'] = current + 1
            else:
                node.extra_metadata = {'content_version': 1}

        # Update timestamp
        if isinstance(node.extra_metadata, dict):
            node.extra_metadata['last_updated'] = datetime.utcnow().isoformat()

        self.db.commit()

        version = node.extra_metadata.get('content_version', 1) if node.extra_metadata else 1
        print(f"  ✓ Content version: {version}")
        print(f"  ✓ Cache automatically invalidated")

    def _verify_content(self, node):
        """Verify content was indexed correctly"""
        chunks = self.db.query(ContentChunk).filter(
            ContentChunk.node_id == node.id
        ).all()

        print(f"  ✓ Verified: {len(chunks)} chunks in database")

        # Check for specific content (if Statistical Inference)
        if node.title == 'Statistical Inference':
            bouchaud_chunks = [c for c in chunks if 'bouchaud' in c.chunk_text.lower()]
            heavy_tail_chunks = [c for c in chunks if 'heavy-tailed' in c.chunk_text.lower()]

            print(f"  ✓ Bouchaud content: {len(bouchaud_chunks)} chunks")
            print(f"  ✓ Heavy-tailed content: {len(heavy_tail_chunks)} chunks")

            if len(bouchaud_chunks) == 0:
                print(f"  ⚠️  Warning: No Bouchaud content found")
