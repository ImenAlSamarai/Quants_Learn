"""
Test script to verify web content is being retrieved in RAG queries
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from app.services.vector_store import vector_store

def test_web_content_retrieval():
    """Test that web content from innovation-options.com is searchable"""

    print("="*80)
    print("TEST: Web Content Retrieval")
    print("="*80)

    # Test topics that should match the indexed web content
    test_topics = [
        "innovation options",
        "option mindset",
        "innovation engine",
        "technology adoption lifecycle",
        "NPV trap",
        "real options"
    ]

    for topic in test_topics:
        print(f"\n🔍 Searching for: '{topic}'")
        print("-" * 60)

        # Search all namespaces (books + web)
        results = vector_store.search_all_namespaces(
            query=topic,
            top_k=5,
            namespaces=['', 'web_resource']
        )

        if results:
            print(f"✅ Found {len(results)} results")

            # Show top 3 results
            for i, match in enumerate(results[:3], 1):
                score = match['score']
                namespace = match.get('source_namespace', 'default')
                source = match.get('metadata', {}).get('source', 'Unknown')
                text_preview = match.get('text', '')[:100].replace('\n', ' ')

                source_type = "🌐 WEB" if namespace == 'web_resource' else "📖 BOOK"

                print(f"\n  {i}. {source_type} | Score: {score:.3f} | Source: {source}")
                print(f"     Preview: \"{text_preview}...\"")

                if namespace == 'web_resource':
                    url = match.get('metadata', {}).get('url', 'N/A')
                    print(f"     URL: {url}")
        else:
            print(f"❌ No results found")

    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)

if __name__ == "__main__":
    test_web_content_retrieval()
