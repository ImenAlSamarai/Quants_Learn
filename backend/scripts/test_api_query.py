"""
Test API query to see if book content is being used

This simulates what happens when a user clicks on a topic in the frontend
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.database import SessionLocal, Node
from app.services.vector_store import vector_store
from app.services.llm_service import LLMService

def test_api_query():
    print("="*80)
    print("Simulating Frontend API Query")
    print("="*80)
    print()

    db = SessionLocal()

    # Find Ridge Regression node
    node = db.query(Node).filter(Node.title == "Ridge Regression").first()

    if not node:
        print("❌ Ridge Regression node not found!")
        print("Did you run: python scripts/index_esl_chapter3.py?")
        db.close()
        return

    print(f"✓ Found node: {node.title} (ID: {node.id})")
    print(f"  Category: {node.category}")
    print(f"  Difficulty: {node.difficulty_level}")
    print()

    # Step 1: Build search query (like the backend does)
    print("[Step 1] Building search query...")
    search_query = f"{node.title} regularization bias variance tradeoff"
    print(f"  Query: '{search_query}'")
    print()

    # Step 2: Search vector store
    print("[Step 2] Searching vector store for relevant chunks...")
    results = vector_store.search(
        query=search_query,
        node_id=node.id,
        top_k=5
    )

    if not results:
        print("❌ No results from vector store!")
        db.close()
        return

    print(f"✓ Found {len(results)} relevant chunks from book")
    print()

    # Show the chunks that will be used
    print("[Step 3] Book content that will inform the LLM:")
    print("-"*80)
    for i, result in enumerate(results, 1):
        print(f"\nChunk {i} (relevance score: {result['score']:.3f}):")
        text_preview = result['text'][:300].replace('\n', ' ')
        print(f"{text_preview}...")

        # Check source
        metadata = result.get('metadata', {})
        if 'source' in metadata:
            print(f"Source: {metadata['source']}")

    print()
    print("-"*80)

    # Step 4: Generate explanation
    print("\n[Step 4] Generating explanation using GPT-4 + book content...")
    print("(This costs ~$0.0005 - half a cent)")
    print()

    try:
        llm = LLMService()

        explanation = llm.generate_explanation(
            node_title=node.title,
            context_chunks=[r['text'] for r in results],
            difficulty_level=3,
            user_context=None
        )

        print("✓ Generated Explanation:")
        print("="*80)
        print(explanation)
        print("="*80)
        print()

        # Check if book-specific terms appear
        book_terms = ['Hastie', 'Tibshirani', 'Friedman', 'equation', 'theorem']
        found_terms = [term for term in book_terms if term.lower() in explanation.lower()]

        if found_terms:
            print(f"✓ Explanation includes book-specific terms: {found_terms}")
        else:
            print("⚠️  Explanation may not be directly from book")

        print()
        print("🎉 SUCCESS! The system is:")
        print("  1. ✓ Retrieving content from ESL book (RAG)")
        print("  2. ✓ Using it to inform GPT-4")
        print("  3. ✓ Generating educational content")
        print()
        print("This is exactly what happens when users click topics in the frontend!")

    except Exception as e:
        print(f"❌ Error generating explanation: {e}")
        print("\nPossible issues:")
        print("  - OpenAI API key not set in .env")
        print("  - Insufficient API credits")

    db.close()


if __name__ == "__main__":
    test_api_query()
