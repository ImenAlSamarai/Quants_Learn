#!/usr/bin/env python3
"""
Quick script to check if insights data exists in database
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.database import SessionLocal, TopicInsights, Node
from sqlalchemy import func

def check_insights():
    db = SessionLocal()

    try:
        # Count total insights
        total_insights = db.query(func.count(TopicInsights.id)).scalar()

        print("=" * 80)
        print("INSIGHTS DATA CHECK")
        print("=" * 80)
        print()

        if total_insights == 0:
            print("❌ NO INSIGHTS DATA FOUND")
            print()
            print("The topic_insights table exists but is empty.")
            print("You need to run: python scripts/generate_all_insights.py")
            print()
            return False

        print(f"✅ FOUND {total_insights} INSIGHTS IN DATABASE")
        print()
        print("Topics with insights:")
        print("-" * 80)

        # Get all insights with topic names
        insights = db.query(TopicInsights, Node).join(Node).all()

        for insight, node in insights:
            num_tips = len(insight.practical_tips) if insight.practical_tips else 0
            num_limitations = len(insight.limitations) if insight.limitations else 0
            num_comparisons = len(insight.method_comparisons) if insight.method_comparisons else 0
            num_when_to_use = len(insight.when_to_use) if insight.when_to_use else 0

            print(f"  • {node.title} (ID: {node.id})")
            print(f"    - When to use: {num_when_to_use} scenarios")
            print(f"    - Limitations: {num_limitations} items")
            print(f"    - Practical tips: {num_tips} tips")
            print(f"    - Comparisons: {num_comparisons} comparisons")
            print()

        print("=" * 80)
        print("✅ Insights feature should work in frontend!")
        print("=" * 80)
        return True

    except Exception as e:
        print(f"❌ ERROR: {e}")
        print()
        print("The topic_insights table might not exist yet.")
        print("Run: python -c \"from app.models.database import init_db; init_db()\"")
        return False

    finally:
        db.close()

if __name__ == "__main__":
    check_insights()
