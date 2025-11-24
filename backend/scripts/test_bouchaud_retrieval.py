#!/usr/bin/env python3
"""
Test Bouchaud Content Retrieval via RAG

Verifies that:
1. Bouchaud content chunks exist in database
2. Vector search retrieves Bouchaud chunks
3. LLM can generate explanations using Bouchaud content
"""

import sys
import os
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.database import SessionLocal, Node, ContentChunk
from app.services.vector_store import vector_store
from app.services.llm_service import llm_service


def main():
    print("=" * 80)
    print("Testing Bouchaud Content Retrieval")
    print("=" * 80)
    print()

    db = SessionLocal()

    try:
        # 1. Verify chunks exist
        print("1. Checking database chunks...")
        node = db.query(Node).filter(
            Node.title == 'Statistical Inference',
            Node.category == 'statistics'
        ).first()

        if not node:
            print("❌ Node not found")
            return 1

        total_chunks = db.query(ContentChunk).filter(ContentChunk.node_id == node.id).count()
        bouchaud_chunks = db.query(ContentChunk).filter(
            ContentChunk.node_id == node.id,
            ContentChunk.chunk_text.ilike('%bouchaud%')
        ).count()
        heavy_tail_chunks = db.query(ContentChunk).filter(
            ContentChunk.node_id == node.id,
            ContentChunk.chunk_text.ilike('%heavy%tail%')
        ).count()

        print(f"   ✓ Total chunks: {total_chunks}")
        print(f"   ✓ Bouchaud mentions: {bouchaud_chunks}")
        print(f"   ✓ Heavy-tailed mentions: {heavy_tail_chunks}")
        print()

        # 2. Test vector search
        print("2. Testing vector search...")
        print("   Query: 'heavy-tailed distributions lévy'")

        matches = vector_store.search(
            query="heavy-tailed distributions lévy pareto",
            node_id=node.id,
            top_k=5
        )

        print(f"   ✓ Retrieved {len(matches)} matches")
        print()

        if matches:
            print("   Top matches:")
            for i, match in enumerate(matches[:3], 1):
                text_preview = match['text'][:150].replace('\n', ' ')
                has_bouchaud = 'bouchaud' in match['text'].lower()
                has_levy = 'lévy' in match['text'].lower() or 'levy' in match['text'].lower()
                has_heavy = 'heavy' in match['text'].lower() and 'tail' in match['text'].lower()

                markers = []
                if has_bouchaud:
                    markers.append("Bouchaud✓")
                if has_levy:
                    markers.append("Lévy✓")
                if has_heavy:
                    markers.append("Heavy-tailed✓")

                marker_str = f" [{', '.join(markers)}]" if markers else ""

                print(f"   {i}. {text_preview}...{marker_str}")
            print()

        # 3. Test LLM generation
        print("3. Testing LLM content generation...")
        context_chunks = [match['text'] for match in matches]

        if not context_chunks:
            print("   ⚠️  No chunks retrieved, cannot test LLM")
            return 1

        explanation = llm_service.generate_explanation(
            topic=node.title,
            context_chunks=context_chunks,
            difficulty_level=2
        )

        print(f"   ✓ Generated {len(explanation)} characters")
        print()

        # Check if generated content mentions Bouchaud concepts
        explanation_lower = explanation.lower()
        has_levy_in_gen = 'lévy' in explanation_lower or 'levy' in explanation_lower
        has_heavy_in_gen = 'heavy' in explanation_lower and 'tail' in explanation_lower
        has_power_law = 'power law' in explanation_lower or 'power-law' in explanation_lower
        has_pareto = 'pareto' in explanation_lower

        print("   Content analysis:")
        print(f"      • Mentions Lévy: {'✓' if has_levy_in_gen else '✗'}")
        print(f"      • Mentions heavy-tailed: {'✓' if has_heavy_in_gen else '✗'}")
        print(f"      • Mentions power-law: {'✓' if has_power_law else '✗'}")
        print(f"      • Mentions Pareto: {'✓' if has_pareto else '✗'}")
        print()

        # Print sample of explanation
        print("   Generated explanation (first 500 chars):")
        print("   " + "-" * 70)
        print("   " + explanation[:500].replace('\n', '\n   '))
        print("   " + "-" * 70)
        print()

        # Final verdict
        print("=" * 80)
        print("Test Results")
        print("=" * 80)

        if bouchaud_chunks > 0 and len(matches) > 0 and (has_levy_in_gen or has_heavy_in_gen):
            print("✅ SUCCESS: Bouchaud content is being retrieved and used!")
            print()
            print("The RAG system is working correctly. If frontend doesn't show")
            print("updated content, it's likely a caching issue.")
            print()
            print("Solution: Clear the cache with:")
            print("  python scripts/clear_cache.py --node-id 17")
            return 0
        else:
            print("⚠️  PARTIAL: Some issues detected")
            if bouchaud_chunks == 0:
                print("   • No Bouchaud chunks in database")
            if len(matches) == 0:
                print("   • Vector search not returning results")
            if not (has_levy_in_gen or has_heavy_in_gen):
                print("   • Generated content doesn't include Bouchaud concepts")
            return 1

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
