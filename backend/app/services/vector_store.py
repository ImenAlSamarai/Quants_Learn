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

    def upsert_web_chunks(
        self,
        chunks: List[str],
        metadata_list: List[Dict[str, Any]],
        namespace: str = "web_resource"
    ) -> List[str]:
        """
        Index web content chunks with embeddings

        Args:
            chunks: List of text chunks (strings)
            metadata_list: List of metadata dicts (one per chunk)
            namespace: Namespace for organizing content

        Returns:
            List of vector IDs
        """
        if not self.available:
            return []

        if len(chunks) != len(metadata_list):
            raise ValueError(f"Chunks ({len(chunks)}) and metadata_list ({len(metadata_list)}) must have same length")

        vectors = []
        vector_ids = []
        total_chunks = len(chunks)

        print(f"  Generating embeddings for {total_chunks} chunks...")
        for i, (chunk, metadata) in enumerate(zip(chunks, metadata_list), 1):
            # Generate embedding with progress
            print(f"    Processing chunk {i}/{total_chunks}...", end='\r')
            embedding = self.generate_embedding(chunk)

            # Generate unique vector ID using URL hash and chunk index
            url = metadata.get('url', 'unknown')
            chunk_index = metadata.get('chunk_index', i-1)
            id_string = f"{url}_{chunk_index}"
            vector_id = hashlib.md5(id_string.encode()).hexdigest()
            vector_ids.append(vector_id)

            # Prepare metadata (ensure text is included and truncated)
            final_metadata = {
                'text': chunk[:1000],  # Store truncated text in metadata
                **metadata
            }

            # Filter out None values (Pinecone doesn't accept null)
            final_metadata = {k: v for k, v in final_metadata.items() if v is not None}

            vectors.append({
                'id': vector_id,
                'values': embedding,
                'metadata': final_metadata
            })

        print()  # New line after progress
        print(f"  ✓ Generated {len(vectors)} embeddings")

        # Upsert to Pinecone with namespace
        if vectors:
            print(f"  Uploading to Pinecone (namespace: {namespace})...")
            self.index.upsert(vectors=vectors, namespace=namespace)
            print(f"  ✓ Upserted {len(vectors)} vectors to namespace '{namespace}'")

        return vector_ids

    def search(
        self,
        query: str,
        node_id: Optional[int] = None,
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None,
        namespace: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant content chunks

        Args:
            query: Search query text
            node_id: Optional filter by node
            top_k: Number of results to return
            filter_metadata: Additional Pinecone filters
            namespace: Optional namespace to search (default: searches default namespace)

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

        # Search in specified namespace
        query_params = {
            'vector': query_embedding,
            'top_k': top_k,
            'include_metadata': True,
            'filter': filter_dict if filter_dict else None
        }

        # Only add namespace if explicitly provided (Pinecone uses default if not specified)
        if namespace is not None:
            query_params['namespace'] = namespace

        results = self.index.query(**query_params)

        # Format results
        matches = []
        for match in results.matches:
            matches.append({
                'id': match.id,
                'score': match.score,
                'text': match.metadata.get('text', ''),
                'metadata': match.metadata,
                'namespace': namespace or 'default'  # Track which namespace this came from
            })

        return matches

    def search_all_namespaces(
        self,
        query: str,
        node_id: Optional[int] = None,
        top_k: int = 10,
        filter_metadata: Optional[Dict[str, Any]] = None,
        namespaces: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search across multiple namespaces and combine results

        Args:
            query: Search query text
            node_id: Optional filter by node
            top_k: Number of results to return PER NAMESPACE
            filter_metadata: Additional Pinecone filters
            namespaces: List of namespaces to search (default: ['', 'web_resource'])

        Returns:
            Combined list of matches from all namespaces, sorted by score
        """
        if not self.available:
            return []

        # Default: search both book content (default namespace) and web content
        if namespaces is None:
            namespaces = ['', 'web_resource']  # Empty string = default namespace

        all_matches = []

        # Search each namespace
        for ns in namespaces:
            ns_param = ns if ns else None  # Convert empty string to None for default namespace
            matches = self.search(
                query=query,
                node_id=node_id,
                top_k=top_k,
                filter_metadata=filter_metadata,
                namespace=ns_param
            )
            # Tag each match with its source namespace
            for match in matches:
                match['source_namespace'] = ns or 'default'
            all_matches.extend(matches)

        # Sort combined results by score (highest first)
        all_matches.sort(key=lambda x: x['score'], reverse=True)

        # Return top_k results overall (not per namespace)
        return all_matches[:top_k]

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
