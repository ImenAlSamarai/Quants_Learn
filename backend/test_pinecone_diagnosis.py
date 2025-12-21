#!/usr/bin/env python3
"""
Diagnostic script to test Pinecone connection and topic coverage
Run this to verify Pinecone is working correctly
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.services.learning_path_service import LearningPathService
from app.models.database import get_db

def test_pinecone_connection():
    """Test if Pinecone is accessible and has data"""
    print("="*80)
    print("🔍 PINECONE CONNECTION DIAGNOSTIC")
    print("="*80)

    service = LearningPathService()

    # Test 1: Check if vector store is available
    print(f"\n1. Vector Store Available: {service.vector_store.available}")

    if not service.vector_store.available:
        print("   ❌ Pinecone is NOT available!")
        return False

    # Test 2: Get index stats
    try:
        stats = service.vector_store.index.describe_index_stats()
        total_vectors = stats.get('total_vector_count', 0)
        print(f"2. Total Vectors in Index: {total_vectors:,}")

        if total_vectors == 0:
            print("   ❌ Index is EMPTY - no vectors indexed!")
            return False
        print(f"   ✅ Index has {total_vectors:,} vectors")
    except Exception as e:
        print(f"   ❌ Error getting index stats: {e}")
        return False

    # Test 3: Test topic coverage check
    print(f"\n3. Testing Topic Coverage for 'machine learning':")
    try:
        coverage = service.check_topic_coverage("machine learning")
        print(f"   - Covered: {coverage['covered']}")
        print(f"   - Confidence: {coverage['confidence']:.2%}")
        if coverage['covered']:
            print(f"   - Source: {coverage['source']}")
            print(f"   - All Sources: {len(coverage.get('all_sources', []))} books")
        else:
            print(f"   ❌ Topic NOT covered (confidence below threshold)")
    except Exception as e:
        print(f"   ❌ Error checking coverage: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Test 4: Test structure generation - use a topic that actually passes threshold
    test_topic = "Python programming"
    test_keywords = ["data manipulation", "NumPy", "pandas"]

    print(f"\n4. Testing Topic Structure Generation for '{test_topic}':")
    try:
        db = next(get_db())

        # First get coverage data
        coverage = service.check_topic_coverage(test_topic)
        print(f"   - Coverage: {coverage['covered']} ({coverage['confidence']:.1%})")

        if not coverage['covered']:
            print(f"   ⚠️  Topic not covered, but still testing structure generation...")

        structure = service.get_or_generate_topic_structure(
            topic_name=test_topic,
            keywords=test_keywords,
            source_books=coverage.get('all_sources', []),
            coverage_data=coverage,  # Pass coverage data
            db=db
        )

        weeks = structure.get('weeks', [])
        print(f"   - Weeks Generated: {len(weeks)}")
        print(f"   - Cached: {structure.get('cached', False)}")

        if len(weeks) == 0:
            print(f"   ❌ No weeks generated!")
            return False

        # Show first week
        first_week = weeks[0]
        print(f"   - Week 1 Title: {first_week.get('title', 'N/A')}")
        print(f"   - Week 1 Sections: {len(first_week.get('sections', []))}")

        # Check for fallback pattern
        if "Introduction to" in first_week.get('title', ''):
            print(f"   ⚠️  WARNING: Detected fallback structure (Introduction to...)")
            print(f"   This means the LLM call failed or returned invalid JSON")
            return False

        print(f"   ✅ Structure generated successfully")

    except Exception as e:
        print(f"   ❌ Error generating structure: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("\n" + "="*80)
    print("✅ ALL TESTS PASSED - Pinecone is working correctly")
    print("="*80)
    return True


if __name__ == "__main__":
    success = test_pinecone_connection()
    sys.exit(0 if success else 1)
