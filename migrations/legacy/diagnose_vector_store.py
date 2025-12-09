#!/usr/bin/env python3
"""
Diagnose vector store search issues
"""

import sys
sys.path.insert(0, '.')

from app.services.vector_store import vector_store
from app.services.llm_service import llm_service

def diagnose_vector_store():
    print("=" * 80)
    print(" VECTOR STORE DIAGNOSTIC")
    print("=" * 80)
    print()

    # Step 1: Check if vector store is available
    print("1. Vector Store Availability:")
    print("-" * 80)
    print(f"  Available: {vector_store.available}")
    print(f"  Index name: {vector_store.index_name}")
    print()

    if not vector_store.available:
        print("❌ Vector store not available - cannot proceed with diagnostics")
        return

    # Step 2: Get index statistics
    print("2. Index Statistics:")
    print("-" * 80)
    try:
        stats = vector_store.get_index_stats()
        print(f"  Total vectors: {stats.get('total_vector_count', 0)}")
        print(f"  Namespaces: {stats.get('namespaces', {})}")
        print(f"  Dimension: {stats.get('dimension', 'unknown')}")

        total_vectors = stats.get('total_vector_count', 0)
        if total_vectors == 0:
            print()
            print("  ⚠️  WARNING: Index is EMPTY! No vectors indexed.")
            print("  This explains why searches return low scores.")
            print("  You need to index your book content first.")
            print()
            print("  To index content, run:")
            print("    python manage.py update-content --node-id <NODE_ID>")
            return
        elif total_vectors < 100:
            print(f"  ⚠️  WARNING: Only {total_vectors} vectors - index might be incomplete")
        else:
            print(f"  ✓ Index has {total_vectors} vectors")
    except Exception as e:
        print(f"  ❌ Error getting stats: {e}")
    print()

    # Step 3: Test search with known good query
    print("3. Test Search - 'machine learning':")
    print("-" * 80)
    try:
        results = vector_store.search(query="machine learning", top_k=5)
        print(f"  Results found: {len(results)}")

        if results:
            print()
            print("  Top 3 matches:")
            for i, match in enumerate(results[:3], 1):
                score = match['score']
                text_preview = match['text'][:150].replace('\n', ' ')
                source = match['metadata'].get('source', 'Unknown')
                node_id = match['metadata'].get('node_id', 'Unknown')

                print(f"    {i}. Score: {score:.4f} | Source: {source} | Node: {node_id}")
                print(f"       Text: {text_preview}...")
                print()
        else:
            print("  ⚠️  No results found for 'machine learning'")
            print("  This is unexpected if you have ML/DL books indexed!")
    except Exception as e:
        print(f"  ❌ Error searching: {e}")
    print()

    # Step 4: Test search with more queries
    print("4. Test Multiple Queries:")
    print("-" * 80)

    test_queries = [
        "deep learning",
        "neural networks",
        "statistics",
        "probability",
        "stochastic calculus",
        "time series",
        "regression"
    ]

    print(f"  Testing {len(test_queries)} queries...")
    print()

    for query in test_queries:
        try:
            results = vector_store.search(query=query, top_k=3)
            if results:
                best_score = results[0]['score']
                best_source = results[0]['metadata'].get('source', 'Unknown')

                status = "✓" if best_score > 0.7 else "⚠️ " if best_score > 0.5 else "✗"
                print(f"  {status} '{query}': score={best_score:.3f}, source={best_source}")
            else:
                print(f"  ✗ '{query}': NO RESULTS")
        except Exception as e:
            print(f"  ✗ '{query}': ERROR - {e}")
    print()

    # Step 5: Check embedding generation
    print("5. Test Embedding Generation:")
    print("-" * 80)
    try:
        test_text = "This is a test sentence about machine learning."
        embedding = vector_store.generate_embedding(test_text)

        print(f"  Embedding dimension: {len(embedding)}")
        print(f"  First 5 values: {embedding[:5]}")
        print(f"  Expected dimension: 1536 (for text-embedding-ada-002)")

        if len(embedding) != 1536:
            print(f"  ⚠️  WARNING: Unexpected dimension! Expected 1536, got {len(embedding)}")
        else:
            print("  ✓ Embedding generation working correctly")
    except Exception as e:
        print(f"  ❌ Error generating embedding: {e}")
    print()

    print("=" * 80)
    print(" DIAGNOSTIC COMPLETE")
    print("=" * 80)
    print()

    # Recommendations
    print("RECOMMENDATIONS:")
    print()

    if total_vectors == 0:
        print("  1. Your vector store is EMPTY - you need to index your books")
        print("  2. Run: python manage.py update-content --node-id <NODE_ID>")
        print("  3. Do this for each book/topic node you have")
    elif total_vectors < 100:
        print("  1. Your index might be incomplete")
        print("  2. Check how many nodes you have vs how many are indexed")
        print("  3. Re-index any missing content")
    else:
        print("  1. Check the test query scores above")
        print("  2. If scores are consistently < 0.5, there might be an embedding mismatch")
        print("  3. If scores are 0.5-0.7 for good matches, lower your threshold")

if __name__ == '__main__':
    diagnose_vector_store()
