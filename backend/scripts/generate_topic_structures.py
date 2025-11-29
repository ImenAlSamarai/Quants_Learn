"""
Generate and cache learning structures for covered topics

This script:
1. Creates the topic_structures table if needed
2. Generates weeks/sections structure for each covered topic
3. Caches in database for instant retrieval

Usage:
    python scripts/generate_topic_structures.py

Cost: ~$0.05 total (8 topics × $0.006 each with gpt-4o-mini)
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.database import SessionLocal, TopicStructure, init_db
from app.services.learning_path_service import learning_path_service

def main():
    print("\n" + "="*80)
    print("Topic Structure Generator - Smart Caching with GPT-4o-mini")
    print("="*80 + "\n")

    # Initialize database (creates table if not exists)
    print("📦 Initializing database...")
    init_db()
    print("✅ Database ready\n")

    db = SessionLocal()

    try:
        # Define your 8 covered topics (from your coverage analysis)
        topics = [
            {
                "name": "algorithmic strategies",
                "keywords": ["trading algorithms", "algorithmic strategies", "execution algorithms", "TWAP", "VWAP"]
            },
            {
                "name": "statistical techniques",
                "keywords": ["statistical methods", "hypothesis testing", "regression", "time series"]
            },
            {
                "name": "machine learning techniques",
                "keywords": ["supervised learning", "model training", "feature engineering", "neural networks"]
            },
            {
                "name": "data analysis",
                "keywords": ["data mining", "exploratory analysis", "visualization", "feature extraction"]
            },
            {
                "name": "performance analysis",
                "keywords": ["performance metrics", "benchmarking", "optimization", "profiling"]
            },
            {
                "name": "risk management",
                "keywords": ["risk metrics", "VaR", "stress testing", "hedging strategies"]
            },
            {
                "name": "quantitative finance theory",
                "keywords": ["pricing models", "derivatives", "portfolio theory", "stochastic calculus"]
            },
            {
                "name": "cloud computing",
                "keywords": ["AWS", "Azure", "distributed systems", "scalability", "cloud architecture"]
            }
        ]

        print(f"🎯 Generating structures for {len(topics)} topics...\n")

        for i, topic_config in enumerate(topics, 1):
            topic_name = topic_config["name"]
            keywords = topic_config["keywords"]

            print(f"\n[{i}/{len(topics)}] Processing: {topic_name}")
            print(f"Keywords: {', '.join(keywords[:3])}...")

            # Get or generate structure (cache-first!)
            structure = learning_path_service.get_or_generate_topic_structure(
                topic_name=topic_name,
                keywords=keywords,
                source_books=[],  # Will be fetched from coverage check
                db=db
            )

            if structure['cached']:
                print(f"   ✅ Retrieved from cache (instant, $0)")
            else:
                weeks_count = len(structure['weeks'])
                sections_count = sum(len(w['sections']) for w in structure['weeks'])
                print(f"   ✅ Generated and cached ({weeks_count} weeks, {sections_count} sections, ~$0.006)")

        print("\n" + "="*80)
        print("✅ All topic structures generated and cached!")
        print("="*80)

        # Show cache statistics
        total_cached = db.query(TopicStructure).filter(TopicStructure.is_valid == True).count()
        print(f"\n📊 Cache Statistics:")
        print(f"   Total cached structures: {total_cached}")
        print(f"   Cost for next {total_cached} users: $0 (FREE!)")
        print(f"\n💡 Users can now access these topics instantly via:")
        print(f"   GET /api/users/topics/{{topic_name}}/structure")
        print()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        db.close()


if __name__ == "__main__":
    main()
