"""
Comprehensive Diagnostic for Content Generation Pipeline

Checks every step:
1. Nodes in Statistics category
2. Cache entries for those nodes
3. Chunks indexed for Statistical Inference
4. Vector search retrieval
5. Actual content in chunks

Usage:
    python scripts/diagnose_content_pipeline.py
"""

import os
import sys
from pathlib import Path

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.models.database import SessionLocal, Node, ContentChunk, GeneratedContent
from app.services.vector_store import VectorStoreService
from app.services.llm_service import LLMService

def print_section(title):
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80)

def diagnose_nodes(db):
    """Check Statistics nodes"""
    print_section("STEP 1: Statistics Nodes in Database")

    nodes = db.query(Node).filter(Node.category == 'statistics').all()

    if not nodes:
        print("❌ No Statistics nodes found!")
        return []

    print(f"✓ Found {len(nodes)} Statistics nodes:\n")

    for node in nodes:
        print(f"  ID: {node.id}")
        print(f"  Title: {node.title}")
        print(f"  Category: {node.category}")
        print(f"  Content Path: {node.content_path}")
        print(f"  Learning Path: {node.learning_path}")
        print(f"  Sequence: {node.sequence_order}")
        print(f"  Tags: {node.tags}")
        print()

    return nodes

def diagnose_cache(db, nodes):
    """Check cached content for Statistics nodes"""
    print_section("STEP 2: Cached Generated Content")

    node_ids = [n.id for n in nodes]

    cached = db.query(GeneratedContent).filter(
        GeneratedContent.node_id.in_(node_ids)
    ).all()

    if not cached:
        print("✓ No cached content found (cache is clear)")
        return

    print(f"⚠️  Found {len(cached)} cached entries:\n")

    for entry in cached:
        node = next((n for n in nodes if n.id == entry.node_id), None)
        node_title = node.title if node else "Unknown"

        print(f"  Node: {node_title} (ID: {entry.node_id})")
        print(f"  Type: {entry.content_type}")
        print(f"  Difficulty: {entry.difficulty_level}")
        print(f"  Created: {entry.created_at}")
        print(f"  Valid: {entry.is_valid}")
        print(f"  Preview: {entry.generated_content[:100]}...")
        print()

def diagnose_chunks(db):
    """Check chunks for Statistical Inference"""
    print_section("STEP 3: Chunks for Statistical Inference")

    node = db.query(Node).filter(Node.title == 'Statistical Inference').first()

    if not node:
        print("❌ Statistical Inference node not found!")
        return None

    print(f"✓ Node ID: {node.id}")
    print(f"  Category: {node.category}")
    print(f"  Content Path: {node.content_path}")
    print(f"  Learning Path: {node.learning_path}")
    print()

    chunks = db.query(ContentChunk).filter(
        ContentChunk.node_id == node.id
    ).all()

    print(f"✓ Found {len(chunks)} chunks\n")

    # Search for Bouchaud-related content
    bouchaud_chunks = [c for c in chunks if 'bouchaud' in c.content.lower()]
    heavy_tail_chunks = [c for c in chunks if 'heavy-tailed' in c.content.lower() or 'heavy tail' in c.content.lower()]
    levy_chunks = [c for c in chunks if 'lévy' in c.content.lower() or 'levy' in c.content.lower()]

    print(f"  Bouchaud mentions: {len(bouchaud_chunks)} chunks")
    print(f"  Heavy-tailed mentions: {len(heavy_tail_chunks)} chunks")
    print(f"  Lévy mentions: {len(levy_chunks)} chunks")
    print()

    if bouchaud_chunks:
        print("Sample Bouchaud chunk:")
        print("-" * 80)
        print(bouchaud_chunks[0].content[:500])
        print("-" * 80)
        print()

    return node

def diagnose_vector_search(node):
    """Test vector search retrieval"""
    print_section("STEP 4: Vector Search Retrieval")

    if not node:
        print("⚠️  Skipping (no node)")
        return

    try:
        vector_store = VectorStoreService()

        if not vector_store.available:
            print("⚠️  Pinecone not available")
            return

        # Test search with relevant query - CORRECT method signature
        print(f"Testing query for node {node.id}: '{node.title}'\n")

        # This is how content.py actually searches
        results = vector_store.search(
            query=f"{node.title} heavy-tailed distributions",
            node_id=node.id,
            top_k=5
        )

        print(f"✓ Retrieved {len(results)} results\n")

        if not results:
            print("❌ No results found! This is the problem.")
            print("   Possible causes:")
            print("   1. Chunks not indexed in Pinecone")
            print("   2. Wrong node_id filter")
            print("   3. Pinecone index out of sync with database")
            print()
            return

        for i, result in enumerate(results, 1):
            print(f"Result {i}:")
            print(f"  Score: {result.get('score', 0):.4f}")
            text = result.get('text', '')
            print(f"  Preview: {text[:200]}...")
            has_bouchaud = 'bouchaud' in text.lower()
            has_heavy_tail = 'heavy-tailed' in text.lower() or 'heavy tail' in text.lower()
            print(f"  Has Bouchaud: {'✓' if has_bouchaud else '✗'}")
            print(f"  Has Heavy-tail: {'✓' if has_heavy_tail else '✗'}")
            print()

    except Exception as e:
        print(f"❌ Vector search failed: {e}")
        import traceback
        traceback.print_exc()

def diagnose_generation(db, node):
    """Test actual content generation"""
    print_section("STEP 5: Test Content Generation")

    if not node:
        print("⚠️  Skipping (no node)")
        return

    try:
        vector_store = VectorStoreService()
        llm_service = LLMService()

        if not vector_store.available:
            print("⚠️  Skipping (Pinecone not available)")
            return

        print("Generating explanation for Statistical Inference (difficulty 2)...\n")

        # Get context chunks - CORRECT method signature matching content.py
        search_results = vector_store.search(
            query=f"{node.title} {node.description or ''}",
            node_id=node.id,
            top_k=10
        )

        context_chunks = [r['text'] for r in search_results]  # 'text' not 'content'

        print(f"✓ Retrieved {len(context_chunks)} context chunks")

        if not context_chunks:
            print("❌ No context chunks retrieved! Content generation will fail.")
            print("   This is why frontend shows old content.")
            print()
            return

        # Check if any contain Bouchaud content
        bouchaud_in_context = any('bouchaud' in c.lower() for c in context_chunks)
        heavy_tail_in_context = any('heavy-tailed' in c.lower() or 'heavy tail' in c.lower() for c in context_chunks)

        print(f"  Bouchaud in context: {'✓' if bouchaud_in_context else '✗'}")
        print(f"  Heavy-tailed in context: {'✓' if heavy_tail_in_context else '✗'}")
        print()

        if not bouchaud_in_context and not heavy_tail_in_context:
            print("⚠️  WARNING: Context chunks don't contain Bouchaud content!")
            print("   This means reindexing didn't work or chunks weren't uploaded to Pinecone.")
            print()

        # Generate explanation
        explanation = llm_service.generate_explanation(
            topic=node.title,
            context_chunks=context_chunks,
            difficulty=2
        )

        print("Generated Explanation Preview:")
        print("-" * 80)
        print(explanation[:800])
        print("-" * 80)
        print()

        # Check if generated content mentions Bouchaud concepts
        explanation_lower = explanation.lower()
        has_heavy_tail = 'heavy-tailed' in explanation_lower or 'heavy tail' in explanation_lower
        has_levy = 'lévy' in explanation_lower or 'levy' in explanation_lower
        has_pareto = 'pareto' in explanation_lower
        has_power_law = 'power law' in explanation_lower or 'power-law' in explanation_lower

        print("Bouchaud Concepts in Generated Content:")
        print(f"  Heavy-tailed: {'✓' if has_heavy_tail else '✗'}")
        print(f"  Lévy: {'✓' if has_levy else '✗'}")
        print(f"  Pareto: {'✓' if has_pareto else '✗'}")
        print(f"  Power law: {'✓' if has_power_law else '✗'}")

        if not any([has_heavy_tail, has_levy, has_pareto, has_power_law]):
            print("\n❌ PROBLEM FOUND: Generated content missing Bouchaud concepts!")
            print("   Even though we have context, LLM isn't using it properly.")

    except Exception as e:
        print(f"❌ Content generation failed: {e}")
        import traceback
        traceback.print_exc()

def main():
    db = SessionLocal()

    try:
        print_section("Content Pipeline Diagnostic")
        print("Checking all steps from database to generated content...")

        # Step 1: Check nodes
        nodes = diagnose_nodes(db)

        if not nodes:
            print("\n❌ Cannot continue without nodes")
            return

        # Step 2: Check cache
        diagnose_cache(db, nodes)

        # Step 3: Check chunks
        node = diagnose_chunks(db)

        # Step 4: Test vector search
        diagnose_vector_search(node)

        # Step 5: Test generation
        diagnose_generation(db, node)

        print_section("Diagnostic Complete")
        print("\nCheck the output above to identify where the pipeline fails.")
        print("\nCommon issues:")
        print("  1. Cache not cleared → Run clear_generated_content_cache.py")
        print("  2. Chunks missing Bouchaud → Reindex failed")
        print("  3. Vector search not finding chunks → Pinecone sync issue")
        print("  4. Generation works but frontend shows old → Frontend cache")

    finally:
        db.close()

if __name__ == "__main__":
    main()
