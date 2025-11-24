"""
Clear Cache Command

Clears generated content cache.
Consolidates: clear_generated_content_cache.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.models.database import SessionLocal, Node, GeneratedContent


class ClearCacheCommand:
    """Clear generated content cache"""

    def __init__(self):
        self.db = None

    def run(self, node_id=None, category=None, clear_all=False):
        """Clear cache for node, category, or all"""
        self.db = SessionLocal()

        try:
            print("=" * 80)
            print(" CLEAR CACHE")
            print("=" * 80)
            print()

            if node_id:
                return self._clear_node(node_id)
            elif category:
                return self._clear_category(category)
            elif clear_all:
                return self._clear_all()

        finally:
            if self.db:
                self.db.close()

    def _clear_node(self, node_id):
        """Clear cache for specific node"""
        node = self.db.query(Node).filter(Node.id == node_id).first()
        if not node:
            print(f"❌ Node {node_id} not found")
            return 1

        print(f"Node: {node.title} (ID: {node_id})")

        count = self.db.query(GeneratedContent).filter(
            GeneratedContent.node_id == node_id
        ).count()

        if count == 0:
            print("  No cached content")
            return 0

        print(f"  Found {count} cached entries")

        self.db.query(GeneratedContent).filter(
            GeneratedContent.node_id == node_id
        ).delete()
        self.db.commit()

        print(f"  ✓ Deleted {count} entries")
        return 0

    def _clear_category(self, category):
        """Clear cache for category"""
        nodes = self.db.query(Node).filter(
            Node.category.ilike(f'%{category}%')
        ).all()

        if not nodes:
            print(f"❌ No nodes found in category '{category}'")
            return 1

        print(f"Category: {category}")
        print(f"  Found {len(nodes)} nodes")

        node_ids = [n.id for n in nodes]

        count = self.db.query(GeneratedContent).filter(
            GeneratedContent.node_id.in_(node_ids)
        ).count()

        if count == 0:
            print("  No cached content")
            return 0

        print(f"  Found {count} cached entries")

        self.db.query(GeneratedContent).filter(
            GeneratedContent.node_id.in_(node_ids)
        ).delete()
        self.db.commit()

        print(f"  ✓ Deleted {count} entries")
        return 0

    def _clear_all(self):
        """Clear all cache"""
        count = self.db.query(GeneratedContent).count()

        if count == 0:
            print("  No cached content")
            return 0

        print(f"⚠️  WARNING: Clearing ALL cached content ({count} entries)")
        print()

        response = input("Are you sure? (yes/no): ")
        if response.lower() != 'yes':
            print("Cancelled")
            return 0

        self.db.query(GeneratedContent).delete()
        self.db.commit()

        print(f"  ✓ Deleted {count} entries")
        return 0
