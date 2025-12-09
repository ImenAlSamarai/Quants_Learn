"""
Verify that Chapters 4 and 7 have been indexed correctly

Checks:
1. Database has the new nodes
2. Pinecone has vectors for the nodes
3. RAG retrieval works for new topics
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.database import SessionLocal, Node, ContentChunk
from app.services.vector_store import vector_store
from app.services.llm_service import LLMService


def verify_indexing():
    print("=" * 80)
    print("Verifying Chapters 4 and 7 Indexing")
    print("=" * 80)
    print()

    db = SessionLocal()

    # Topics we expect to find
    expected_topics = {
        'Chapter 4 - Classification': [
            'Logistic Regression',
            'Linear Discriminant Analysis',
            'Classification Performance Metrics'
        ],
        'Chapter 7 - Model Assessment': [
            'Bias-Variance Decomposition',
            'Cross-Validation Methods',
            'Bootstrap Methods',
            'Model Selection Criteria'
        ]
    }

    all_success = True

    for chapter, topics in expected_topics.items():
        print(f"\n{chapter}")
        print("-" * 80)

        for topic_name in topics:
            node = db.query(Node).filter(Node.title == topic_name).first()

            if not node:
                print(f"❌ {topic_name}: NOT FOUND in database")
                all_success = False
                continue

            # Check chunks in database
            chunk_count = db.query(ContentChunk).filter(ContentChunk.node_id == node.id).count()

            if chunk_count == 0:
                print(f"⚠️  {topic_name}: Found in DB but NO CHUNKS")
                all_success = False
                continue

            # Try to search in Pinecone
            try:
                search_results = vector_store.search(
                    query=topic_name,
                    node_id=node.id,
                    top_k=3
                )

                if not search_results:
                    print(f"⚠️  {topic_name}: {chunk_count} chunks in DB but NO VECTORS in Pinecone")
                    all_success = False
                else:
                    print(f"✓ {topic_name}: {chunk_count} chunks, vectors indexed ✓")

            except Exception as e:
                print(f"❌ {topic_name}: Error searching Pinecone: {e}")
                all_success = False

    print()
    print("=" * 80)

    if all_success:
        print("✅ ALL CHECKS PASSED!")
        print()
        print("All topics are properly indexed and searchable.")
        print()
        print("Next steps:")
        print("  1. Start the backend: cd backend && uvicorn app.main:app --reload")
        print("  2. Start the frontend: cd frontend && npm run dev")
        print("  3. Open browser to http://localhost:5173")
        print("  4. Navigate to Machine Learning category")
        print("  5. You should see all topics including the new ones!")
    else:
        print("❌ SOME CHECKS FAILED")
        print()
        print("Please review the errors above and re-run indexing if needed.")
        print()
        print("To re-index:")
        print("  cd backend")
        print("  python scripts/index_esl_chapter4.py")
        print("  python scripts/index_esl_chapter7.py")

    print()
    db.close()


def test_rag_retrieval():
    """Test RAG retrieval for one topic from each chapter"""
    print("\n" + "=" * 80)
    print("Testing RAG Retrieval")
    print("=" * 80)
    print()

    db = SessionLocal()

    test_topics = [
        ('Logistic Regression', 'logistic regression maximum likelihood'),
        ('Cross-Validation Methods', 'k-fold cross validation')
    ]

    for topic_name, query in test_topics:
        print(f"\nTesting: {topic_name}")
        print("-" * 80)

        node = db.query(Node).filter(Node.title == topic_name).first()

        if not node:
            print(f"❌ Topic '{topic_name}' not found")
            continue

        try:
            # Search for relevant chunks
            results = vector_store.search(
                query=query,
                node_id=node.id,
                top_k=2
            )

            if results:
                print(f"✓ Retrieved {len(results)} chunks")
                print(f"\nFirst chunk preview:")
                print(results[0]['text'][:300] + "...")
                print()
            else:
                print(f"⚠️  No results found for query: '{query}'")

        except Exception as e:
            print(f"❌ Error: {e}")

    db.close()


if __name__ == "__main__":
    verify_indexing()
    test_rag_retrieval()
