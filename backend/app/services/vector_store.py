import pinecone
from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI
from typing import List, Dict, Any, Optional
from app.config.settings import settings
import hashlib


class VectorStoreService:
    """Handles all vector database operations with Pinecone"""

    def __init__(self):
        self.pc = None
        self.openai_client = None
        self.index_name = settings.PINECONE_INDEX_NAME
        self.index = None
        self.available = False
        self._initialize_index()

    def _create_openai_client_with_timeout(self):
        """Create OpenAI client with timeout settings"""
        import httpx
        return OpenAI(
            api_key=settings.OPENAI_API_KEY,
            timeout=httpx.Timeout(60.0, connect=10.0),  # 60s total, 10s connect
            max_retries=2
        )

    def _initialize_index(self):
        """Create index if it doesn't exist and connect to it"""
        try:
            self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
            self.openai_client = self._create_openai_client_with_timeout()

            # Check if index exists
            existing_indexes = [idx.name for idx in self.pc.list_indexes()]

            if self.index_name not in existing_indexes:
                # Create new index
                self.pc.create_index(
                    name=self.index_name,
                    dimension=settings.EMBEDDING_DIMENSION,
                    metric='cosine',
                    spec=ServerlessSpec(
                        cloud='aws',
                        region='us-east-1'
                    )
                )
                print(f"Created new Pinecone index: {self.index_name}")

            # Connect to index
            self.index = self.pc.Index(self.index_name)
            self.available = True
            print(f"Connected to Pinecone index: {self.index_name}")

        except Exception as e:
            print(f"Error initializing Pinecone index: {e}")
            print("Vector store will not be available - content generation will be disabled")
            self.available = False

    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding vector for text using OpenAI"""
        if not self.available:
            return []
        try:
            response = self.openai_client.embeddings.create(
                model=settings.EMBEDDING_MODEL,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            raise

    def generate_vector_id(self, node_id: int, chunk_index: int) -> str:
        """Generate unique vector ID"""
        return f"node_{node_id}_chunk_{chunk_index}"

    def upsert_chunks(
        self,
        chunks: List[Dict[str, Any]],
        node_id: int,
        node_metadata: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        Index content chunks with embeddings

        Args:
            chunks: List of dicts with 'text', 'chunk_index', 'metadata'
            node_id: Associated node ID
            node_metadata: Additional metadata for all chunks

        Returns:
            List of vector IDs
        """
        if not self.available:
            return []

        vectors = []
        vector_ids = []
        total_chunks = len(chunks)

        print(f"  Generating embeddings for {total_chunks} chunks...")
        for i, chunk in enumerate(chunks, 1):
            text = chunk['text']
            chunk_index = chunk['chunk_index']
            chunk_metadata = chunk.get('metadata', {})

            # Generate embedding with progress
            print(f"    Processing chunk {i}/{total_chunks}...", end='\r')
            embedding = self.generate_embedding(text)

            # Create vector ID
            vector_id = self.generate_vector_id(node_id, chunk_index)
            vector_ids.append(vector_id)

            # Prepare metadata
            metadata = {
                'node_id': node_id,
                'chunk_index': chunk_index,
                'text': text[:1000],  # Store truncated text in metadata
                **chunk_metadata
            }

            if node_metadata:
                metadata.update(node_metadata)

            # Filter out None values (Pinecone doesn't accept null)
            metadata = {k: v for k, v in metadata.items() if v is not None}

            vectors.append({
                'id': vector_id,
                'values': embedding,
                'metadata': metadata
            })

        print()  # New line after progress
        print(f"  ✓ Generated {len(vectors)} embeddings")

        # Upsert to Pinecone
        if vectors:
            print(f"  Uploading to Pinecone...")
            self.index.upsert(vectors=vectors)
            print(f"  ✓ Upserted {len(vectors)} vectors for node {node_id}")

        return vector_ids

    def search(
        self,
        query: str,
        node_id: Optional[int] = None,
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant content chunks

        Args:
            query: Search query text
            node_id: Optional filter by node
            top_k: Number of results to return
            filter_metadata: Additional Pinecone filters

        Returns:
            List of matches with text and metadata
        """
        if not self.available:
            return []

        # Generate query embedding
        query_embedding = self.generate_embedding(query)

        # Build filter
        filter_dict = {}
        if node_id:
            filter_dict['node_id'] = node_id
        if filter_metadata:
            filter_dict.update(filter_metadata)

        # Search
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True,
            filter=filter_dict if filter_dict else None
        )

        # Format results
        matches = []
        for match in results.matches:
            matches.append({
                'id': match.id,
                'score': match.score,
                'text': match.metadata.get('text', ''),
                'metadata': match.metadata
            })

        return matches

    def delete_node_vectors(self, node_id: int):
        """Delete all vectors associated with a node"""
        if not self.available:
            return
        try:
            self.index.delete(filter={'node_id': node_id})
            print(f"Deleted vectors for node {node_id}")
        except Exception as e:
            # Ignore "namespace not found" errors (expected on first index)
            if "Namespace not found" in str(e) or "404" in str(e):
                print(f"No existing vectors to delete for node {node_id} (first time indexing)")
            else:
                print(f"Error deleting vectors: {e}")
                raise

    def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the index"""
        if not self.available:
            return {}
        return self.index.describe_index_stats()


# Singleton instance
vector_store = VectorStoreService()
