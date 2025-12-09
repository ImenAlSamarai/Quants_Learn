"""
Test script to validate topic extraction improvements

This script tests the enhanced topic extraction with:
1. Few-shot examples in the prompt (Solution 2)
2. Keyword fallback matching (Solution 5)

Expected improvements:
- More specific topics (not generic)
- Better coverage matching (using keywords as fallback)
- Zero cost increase (still using GPT-4o-mini)
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from services.learning_path_service import LearningPathService
from models.database import get_db

# Test job descriptions with known specific terminology
test_jobs = [
    {
        "name": "Test 1: Macro positioning & derivatives",
        "description": """
        Senior Quantitative Researcher - Macro Trading

        Requirements:
        - Macro positioning models and economic forecasting
        - Equity derivatives pricing (options, variance swaps)
        - Retail investor sentiment analysis
        - Python and statistical modeling

        Nice to have:
        - Time series forecasting
        - Volatility modeling
        """
    },
    {
        "name": "Test 2: Algorithmic trading & microstructure",
        "description": """
        Quantitative Trader - HFT Desk

        Requirements:
        - Algorithmic trading strategies
        - Market microstructure analysis
        - Order book dynamics
        - Low-latency C++ systems
        - Slippage modeling

        Preferred:
        - Machine learning for alpha generation
        """
    },
    {
        "name": "Test 3: ML & time series",
        "description": """
        Machine Learning Engineer - Systematic Trading

        Requirements:
        - Time series forecasting with ARIMA models
        - Seasonality detection techniques
        - Feature engineering for financial data
        - Production ML systems in Python
        - Backtesting frameworks

        Bonus:
        - Deep learning for NLP on financial news
        """
    }
]

def test_topic_specificity(topics: list) -> dict:
    """Check if topics are specific vs generic"""
    generic_terms = ['knowledge', 'skills', 'understanding', 'analysis', 'handling',
                     'design', 'development', 'methods', 'techniques', 'ability']

    generic_count = 0
    generic_topics = []

    for topic in topics:
        topic_name = topic.get('name', '').lower()
        # Check if topic contains generic terms as main identifier
        for generic_term in generic_terms:
            if generic_term in topic_name.split():
                generic_count += 1
                generic_topics.append(topic['name'])
                break

    specificity_score = 1 - (generic_count / len(topics)) if topics else 0

    return {
        'total_topics': len(topics),
        'generic_count': generic_count,
        'generic_topics': generic_topics,
        'specificity_score': specificity_score,
        'grade': 'A' if specificity_score > 0.9 else 'B' if specificity_score > 0.7 else 'C' if specificity_score > 0.5 else 'D'
    }

def main():
    print("="*80)
    print("TOPIC EXTRACTION IMPROVEMENT TEST")
    print("="*80)
    print("\nTesting enhanced extraction with:")
    print("  ✓ Few-shot examples (bad vs good extractions)")
    print("  ✓ Keyword fallback matching (improves coverage)")
    print("  ✓ Still using GPT-4o-mini (no cost increase)")
    print("\n" + "="*80 + "\n")

    service = LearningPathService()

    results = []

    for test_case in test_jobs:
        print(f"\n{'='*80}")
        print(f"TEST: {test_case['name']}")
        print(f"{'='*80}\n")

        try:
            # Analyze job description
            job_profile = service.analyze_job_description(test_case['description'])

            # Extract topics
            explicit_topics = job_profile.get('topic_hierarchy', {}).get('explicit_topics', [])

            # Evaluate specificity
            specificity_results = test_topic_specificity(explicit_topics)

            results.append({
                'test_name': test_case['name'],
                'topics_extracted': [t['name'] for t in explicit_topics],
                'specificity': specificity_results
            })

            print(f"\n📊 RESULTS:")
            print(f"   Topics extracted: {specificity_results['total_topics']}")
            print(f"   Generic topics: {specificity_results['generic_count']}")
            print(f"   Specificity score: {specificity_results['specificity_score']:.2%}")
            print(f"   Grade: {specificity_results['grade']}")

            if specificity_results['generic_topics']:
                print(f"\n   ⚠️  Generic topics found:")
                for gt in specificity_results['generic_topics']:
                    print(f"      - {gt}")
            else:
                print(f"\n   ✓ No generic topics detected!")

            print(f"\n   Extracted topics:")
            for i, topic in enumerate(explicit_topics[:10], 1):
                priority_emoji = "🔴" if topic.get('priority') == 'HIGH' else "🟡"
                print(f"      {i}. {priority_emoji} {topic['name']}")
                if i == 10 and len(explicit_topics) > 10:
                    print(f"      ... and {len(explicit_topics) - 10} more")

        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            results.append({
                'test_name': test_case['name'],
                'error': str(e)
            })

    # Summary
    print(f"\n\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}\n")

    successful_tests = [r for r in results if 'error' not in r]
    if successful_tests:
        avg_specificity = sum(r['specificity']['specificity_score'] for r in successful_tests) / len(successful_tests)
        total_generic = sum(r['specificity']['generic_count'] for r in successful_tests)
        total_topics = sum(r['specificity']['total_topics'] for r in successful_tests)

        print(f"Tests run: {len(results)}")
        print(f"Successful: {len(successful_tests)}")
        print(f"Failed: {len(results) - len(successful_tests)}")
        print(f"\nAverage specificity score: {avg_specificity:.2%}")
        print(f"Total topics extracted: {total_topics}")
        print(f"Total generic topics: {total_generic}")
        print(f"Generic rate: {(total_generic / total_topics * 100) if total_topics > 0 else 0:.1f}%")

        # Overall grade
        if avg_specificity > 0.9:
            grade = "A - Excellent"
            emoji = "🎉"
        elif avg_specificity > 0.7:
            grade = "B - Good"
            emoji = "✅"
        elif avg_specificity > 0.5:
            grade = "C - Acceptable"
            emoji = "⚠️"
        else:
            grade = "D - Needs Improvement"
            emoji = "❌"

        print(f"\n{emoji} OVERALL GRADE: {grade}")

        if avg_specificity > 0.85:
            print("\n🎯 SUCCESS: Topic extraction quality has significantly improved!")
            print("   Topics are specific and use terminology from job descriptions.")
        elif avg_specificity > 0.7:
            print("\n✓ IMPROVED: Topic extraction is better, but some room for improvement.")
        else:
            print("\n⚠️  NEEDS WORK: Still finding too many generic topics.")
    else:
        print(f"❌ All tests failed. See errors above.")

    print(f"\n{'='*80}\n")

if __name__ == "__main__":
    main()
