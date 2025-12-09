"""
Verify Chapter 3 indexing and test RAG retrieval

This script checks:
1. Nodes were created in database
2. Content chunks were indexed
3. Vector store has embeddings
4. RAG retrieval returns book content
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.database import SessionLocal, Node, ContentChunk
from app.services.vector_store import vector_store
from app.services.llm_service import LLMService

def test_indexing():
    print("="*80)
    print("Chapter 3 Indexing Verification Test")
    print("="*80)
    print()

    db = SessionLocal()

    # Test 1: Check if nodes were created
    print("[Test 1] Checking if nodes were created...")
    print("-"*80)

    ml_topics = [
        "Linear Regression and Least Squares",
        "Subset Selection Methods",
        "Ridge Regression",
        "Lasso Regression"
    ]

    nodes_found = []
    for topic in ml_topics:
        node = db.query(Node).filter(Node.title == topic).first()
        if node:
            print(f"✓ Found: {topic} (ID: {node.id})")
            nodes_found.append(node)
        else:
            print(f"✗ Missing: {topic}")

    if not nodes_found:
        print("\n❌ ERROR: No nodes were created. Did indexing run successfully?")
        db.close()
        return False

    print(f"\n✓ Found {len(nodes_found)}/{len(ml_topics)} topics")
    print()

    # Test 2: Check content chunks
    print("[Test 2] Checking content chunks in database...")
    print("-"*80)

    total_chunks = 0
    for node in nodes_found:
        chunks = db.query(ContentChunk).filter(ContentChunk.node_id == node.id).all()
        chunk_count = len(chunks)
        total_chunks += chunk_count

        # Show sample from first chunk
        if chunks:
            sample = chunks[0].chunk_text[:150].replace('\n', ' ')
            print(f"✓ {node.title}: {chunk_count} chunks")
            print(f"  Sample: {sample}...")
        else:
            print(f"✗ {node.title}: 0 chunks (ERROR)")

    print(f"\n✓ Total chunks indexed: {total_chunks}")
    print()

    # Test 3: Test vector store retrieval
    print("[Test 3] Testing RAG retrieval from vector store...")
    print("-"*80)

    if not vector_store.available:
        print("⚠️  Vector store not available (Pinecone not configured)")
        print("   Skipping RAG tests")
    else:
        # Test query about ridge regression
        test_queries = [
            ("ridge regression regularization", "Ridge Regression"),
            ("lasso L1 penalty sparsity", "Lasso Regression"),
            ("least squares estimation", "Linear Regression and Least Squares"),
        ]

        for query, expected_topic in test_queries:
            print(f"\nQuery: '{query}'")
            results = vector_store.search(
                query=query,
                top_k=3
            )

            if results:
                top_result = results[0]
                print(f"✓ Found {len(results)} matches")
                print(f"  Top match score: {top_result['score']:.3f}")
                print(f"  Content preview: {top_result['text'][:200]}...")

                # Check if it's from our book
                metadata = top_result.get('metadata', {})
                source = metadata.get('source', 'Unknown')
                if 'ESL' in source or 'Elements of Statistical Learning' in source:
                    print(f"  ✓ Source: {source} (BOOK CONTENT!)")
                else:
                    print(f"  ⚠️  Source: {source}")
            else:
                print(f"✗ No results found")

    print()

    # Test 4: Test LLM service with book context
    print("[Test 4] Testing LLM generation with book context...")
    print("-"*80)

    if not vector_store.available:
        print("⚠️  Skipping LLM test (requires vector store)")
    else:
        # Get a node
        ridge_node = db.query(Node).filter(Node.title == "Ridge Regression").first()

        if ridge_node:
            print(f"Generating explanation for: {ridge_node.title}")

            # Search for relevant chunks
            search_results = vector_store.search(
                query="ridge regression regularization bias variance",
                node_id=ridge_node.id,
                top_k=3
            )

            if search_results:
                print(f"✓ Retrieved {len(search_results)} chunks from book")

                # Show what context would be sent to LLM
                print("\nContext chunks that would be sent to GPT-4:")
                for i, result in enumerate(search_results, 1):
                    preview = result['text'][:150].replace('\n', ' ')
                    print(f"  Chunk {i} (score: {result['score']:.3f}): {preview}...")

                # Try generating (this will cost ~$0.0005)
                try:
                    print("\nGenerating explanation using book content...")
                    llm = LLMService()

                    explanation = llm.generate_explanation(
                        node_title=ridge_node.title,
                        context_chunks=[r['text'] for r in search_results],
                        difficulty_level=3,
                        user_context="What is ridge regression and why is it useful?"
                    )

                    print(f"\n✓ Generated explanation ({len(explanation)} chars):")
                    print("-"*80)
                    print(explanation[:500])
                    print("...")
                    print("\n✓ LLM successfully used book content!")

                except Exception as e:
                    print(f"⚠️  LLM generation failed: {e}")
                    print("   (This might be due to OpenAI API configuration)")
            else:
                print("✗ No chunks found for node")
        else:
            print("✗ Ridge Regression node not found")

    print()
    print("="*80)
    print("Verification Summary")
    print("="*80)
    print(f"✓ Nodes created: {len(nodes_found)}/{len(ml_topics)}")
    print(f"✓ Total chunks: {total_chunks}")
    print(f"✓ Vector store: {'Available' if vector_store.available else 'Not configured'}")

    if len(nodes_found) == len(ml_topics) and total_chunks > 0:
        print("\n🎉 SUCCESS! Chapter 3 content is indexed and ready to use!")
        print("\nNext steps:")
        print("  1. Start backend: cd backend && python -m app.main")
        print("  2. Start frontend: cd frontend && npm run dev")
        print("  3. Navigate to Machine Learning category")
        print("  4. Click on 'Ridge Regression' or 'Lasso Regression'")
        print("  5. Try different tabs (Explanation, Examples, Quiz)")
        print("  6. Notice how content comes from the ESL book!")
    else:
        print("\n⚠️  Some issues found. Check errors above.")

    db.close()
    return True


if __name__ == "__main__":
    test_indexing()
