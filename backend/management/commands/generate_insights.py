"""
Generate Insights Command

Generates missing insights for topics.
Consolidates: generate_*_insights.py scripts
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.models.database import SessionLocal, Node, TopicInsights


class GenerateInsightsCommand:
    """Generate missing insights"""

    def __init__(self):
        self.db = None

    def run(self, category=None, all_categories=False):
        """Generate insights for category or all"""
        self.db = SessionLocal()

        try:
            print("=" * 80)
            print(" GENERATE INSIGHTS")
            print("=" * 80)
            print()

            if category:
                return self._generate_for_category(category)
            elif all_categories:
                return self._generate_all()

        finally:
            if self.db:
                self.db.close()

    def _generate_for_category(self, category):
        """Generate insights for category"""
        nodes = self.db.query(Node).filter(
            Node.category.ilike(f'%{category}%')
        ).all()

        if not nodes:
            print(f"❌ No nodes found in category '{category}'")
            return 1

        print(f"Category: {category}")
        print(f"  Found {len(nodes)} nodes")
        print()

        generated = 0
        skipped = 0

        for node in nodes:
            # Check if insights already exist
            existing = self.db.query(TopicInsights).filter(
                TopicInsights.node_id == node.id
            ).count()

            if existing > 0:
                print(f"  ⏭  {node.title}: {existing} insights exist")
                skipped += 1
                continue

            # TODO: Implement actual insights generation
            # For now, just report what would be generated
            print(f"  ⏸  {node.title}: Would generate insights")
            # generated += 1

        print()
        print(f"Summary:")
        print(f"  Generated: {generated}")
        print(f"  Skipped (exist): {skipped}")
        print()
        print("Note: Actual insights generation requires ESL book processing")
        print("      Run existing scripts: python scripts/generate_*_insights.py")

        return 0

    def _generate_all(self):
        """Generate insights for all categories"""
        print("Generating insights for all categories...")
        print()

        categories = self.db.query(Node.category).distinct().all()
        categories = [c[0] for c in categories]

        for category in categories:
            print(f"Category: {category}")
            self._generate_for_category(category)
            print()

        return 0
