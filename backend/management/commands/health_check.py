"""
Health Check Command

Consolidates all diagnostic scripts into single command.
Replaces: diagnose_content_pipeline.py, verify_cache_state.py, etc.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.models.database import SessionLocal, Node, ContentChunk, GeneratedContent, TopicInsights
from app.services.vector_store import VectorStoreService
from app.services.llm_service import LLMService


class HealthCheckCommand:
    """System health diagnostics"""

    def __init__(self):
        self.db = None
        self.issues = []
        self.warnings = []

    def run(self, verbose=False):
        """Run all health checks"""
        self.db = SessionLocal()
        self.verbose = verbose

        try:
            self.print_header("SYSTEM HEALTH CHECK")

            # Run checks
            self.check_database()
            self.check_vector_store()
            self.check_content()
            self.check_cache()
            self.check_insights()

            # Summary
            self.print_summary()

            return 0 if not self.issues else 1

        finally:
            if self.db:
                self.db.close()

    def print_header(self, title):
        print("\n" + "=" * 80)
        print(f" {title}")
        print("=" * 80 + "\n")

    def print_section(self, title):
        print(f"\n{title}")
        print("-" * 80)

    def check_database(self):
        """Check database connection and tables"""
        self.print_section("1. DATABASE CONNECTION")

        try:
            # Count nodes
            node_count = self.db.query(Node).count()
            chunk_count = self.db.query(ContentChunk).count()
            cache_count = self.db.query(GeneratedContent).count()
            insights_count = self.db.query(TopicInsights).count()

            print(f"✓ Database connected")
            print(f"  Nodes: {node_count}")
            print(f"  Chunks: {chunk_count}")
            print(f"  Cached content: {cache_count}")
            print(f"  Insights: {insights_count}")

            if node_count == 0:
                self.issues.append("No nodes in database")
            if chunk_count == 0:
                self.issues.append("No content chunks indexed")

        except Exception as e:
            self.issues.append(f"Database error: {e}")
            print(f"❌ Database error: {e}")

    def check_vector_store(self):
        """Check Pinecone connection"""
        self.print_section("2. VECTOR STORE (Pinecone)")

        try:
            vector_store = VectorStoreService()

            if not vector_store.available:
                self.issues.append("Pinecone not available")
                print("❌ Pinecone not available")
                return

            stats = vector_store.get_index_stats()
            print(f"✓ Pinecone connected")
            print(f"  Index: {vector_store.index_name}")
            if self.verbose and stats:
                print(f"  Stats: {stats}")

        except Exception as e:
            self.issues.append(f"Vector store error: {e}")
            print(f"❌ Vector store error: {e}")

    def check_content(self):
        """Check content indexing for all categories"""
        self.print_section("3. CONTENT INDEXING")

        try:
            # Get all nodes grouped by category
            all_nodes = self.db.query(Node).all()

            if not all_nodes:
                self.issues.append("No nodes in database")
                print("❌ No nodes found in database")
                return

            # Group by category
            by_category = {}
            for node in all_nodes:
                cat = node.category or 'uncategorized'
                if cat not in by_category:
                    by_category[cat] = []
                by_category[cat].append(node)

            print(f"✓ Found {len(all_nodes)} total nodes across {len(by_category)} categories\n")

            # Check each category
            unindexed_nodes = []
            poorly_indexed = []  # Less than 5 chunks

            for category, nodes in sorted(by_category.items()):
                total_chunks = 0
                unindexed_count = 0

                for node in nodes:
                    chunk_count = self.db.query(ContentChunk).filter(
                        ContentChunk.node_id == node.id
                    ).count()

                    total_chunks += chunk_count

                    if chunk_count == 0:
                        unindexed_nodes.append(f"{node.title} (ID: {node.id})")
                        unindexed_count += 1
                    elif chunk_count < 5:
                        poorly_indexed.append(f"{node.title} ({chunk_count} chunks)")

                status = "✓" if unindexed_count == 0 else "⚠️"
                print(f"{status} {category.upper()}: {len(nodes)} nodes, {total_chunks} chunks")

                if unindexed_count > 0:
                    print(f"    ⚠️  {unindexed_count} nodes not indexed")

            # Report issues
            if unindexed_nodes:
                print(f"\n⚠️  {len(unindexed_nodes)} nodes with NO chunks:")
                for node_info in unindexed_nodes[:5]:  # Show first 5
                    print(f"    • {node_info}")
                if len(unindexed_nodes) > 5:
                    print(f"    ... and {len(unindexed_nodes) - 5} more")
                self.warnings.append(f"{len(unindexed_nodes)} nodes not indexed")

            if poorly_indexed:
                print(f"\n⚠️  {len(poorly_indexed)} nodes with < 5 chunks:")
                for node_info in poorly_indexed[:5]:
                    print(f"    • {node_info}")
                if len(poorly_indexed) > 5:
                    print(f"    ... and {len(poorly_indexed) - 5} more")
                self.warnings.append(f"{len(poorly_indexed)} nodes poorly indexed")

            # Special check: Bouchaud content in Statistical Inference
            if self.verbose:
                print("\n📚 Bouchaud Content Check:")
                inference_node = next((n for n in all_nodes if n.title == 'Statistical Inference'), None)
                if inference_node:
                    chunks = self.db.query(ContentChunk).filter(
                        ContentChunk.node_id == inference_node.id
                    ).all()
                    bouchaud_chunks = [c for c in chunks if 'bouchaud' in c.chunk_text.lower()]
                    heavy_tail_chunks = [c for c in chunks if 'heavy-tailed' in c.chunk_text.lower()]

                    print(f"  Statistical Inference: {len(chunks)} total chunks")
                    print(f"    Bouchaud mentions: {len(bouchaud_chunks)} chunks")
                    print(f"    Heavy-tailed mentions: {len(heavy_tail_chunks)} chunks")

        except Exception as e:
            self.issues.append(f"Content check error: {e}")
            print(f"❌ Content check error: {e}")

    def check_cache(self):
        """Check generated content cache state"""
        self.print_section("4. CACHE STATE")

        try:
            total_cache = self.db.query(GeneratedContent).count()
            print(f"  Total cached entries: {total_cache}")

            # Check Statistics cache
            stats_nodes = self.db.query(Node).filter(Node.category == 'statistics').all()
            stats_node_ids = [n.id for n in stats_nodes]

            stats_cache = self.db.query(GeneratedContent).filter(
                GeneratedContent.node_id.in_(stats_node_ids)
            ).count()

            print(f"  Statistics cached: {stats_cache}")

            if self.verbose and stats_cache > 0:
                # Show details
                cached = self.db.query(GeneratedContent).filter(
                    GeneratedContent.node_id.in_(stats_node_ids)
                ).limit(5).all()

                for entry in cached:
                    node = next((n for n in stats_nodes if n.id == entry.node_id), None)
                    if node:
                        has_bouchaud = 'bouchaud' in entry.generated_content.lower() or \
                                     'heavy-tailed' in entry.generated_content.lower()
                        status = "✓ Updated" if has_bouchaud else "✗ Old"
                        print(f"    {node.title} (diff {entry.difficulty_level}): {status}")

        except Exception as e:
            self.issues.append(f"Cache check error: {e}")
            print(f"❌ Cache check error: {e}")

    def check_insights(self):
        """Check insights generation"""
        self.print_section("5. INSIGHTS")

        try:
            total_insights = self.db.query(TopicInsights).count()
            print(f"  Total insights: {total_insights}")

            # Check Statistics insights
            stats_nodes = self.db.query(Node).filter(Node.category == 'statistics').all()
            stats_node_ids = [n.id for n in stats_nodes]

            stats_insights = self.db.query(TopicInsights).filter(
                TopicInsights.node_id.in_(stats_node_ids)
            ).count()

            print(f"  Statistics insights: {stats_insights}")

            missing = len(stats_nodes) - stats_insights
            if missing > 0:
                self.warnings.append(f"{missing} Statistics topics missing insights")
                print(f"  ⚠️  {missing} topics missing insights")

        except Exception as e:
            self.issues.append(f"Insights check error: {e}")
            print(f"❌ Insights check error: {e}")

    def print_summary(self):
        """Print summary and recommendations"""
        self.print_section("SUMMARY")

        if not self.issues and not self.warnings:
            print("✅ All checks passed - System healthy")
            return

        if self.issues:
            print(f"\n❌ Found {len(self.issues)} issues:")
            for issue in self.issues:
                print(f"  • {issue}")

        if self.warnings:
            print(f"\n⚠️  Found {len(self.warnings)} warnings:")
            for warning in self.warnings:
                print(f"  • {warning}")

        print("\nRecommended actions:")
        if "No nodes in database" in str(self.issues):
            print("  → Run content indexing scripts")
        if "Bouchaud content not found" in str(self.warnings):
            print("  → Run: python manage.py update-content --node-id 17")
        if "missing insights" in str(self.warnings):
            print("  → Run: python manage.py generate-insights --category statistics")
