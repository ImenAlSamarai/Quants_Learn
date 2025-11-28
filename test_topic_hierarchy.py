#!/usr/bin/env python3
"""
Test script for the new hierarchical topic detection logic

This script tests the redesigned analyze_job_description() method
to verify that it correctly returns structured topic hierarchy with:
1. Explicit topics (directly mentioned)
2. Implicit topics (typical for role)
3. Priority levels (HIGH/MEDIUM/LOW)
4. Keywords for each topic
"""

import sys
import os
import json

# Add backend to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.learning_path_service import learning_path_service

# Sample job description for a quantitative researcher role
SAMPLE_JOB_DESCRIPTION = """
Quantitative Researcher - Systematic Trading

Requirements:
- Strong background in statistical modeling and time series analysis
- Experience with machine learning for financial markets
- Proficiency in Python and C++
- Knowledge of portfolio optimization techniques
- Backtesting experience with historical market data

Nice to have:
- PhD in Statistics, Mathematics, or related field
- Experience with reinforcement learning
- Familiarity with options pricing models

We're looking for someone who can develop and validate trading strategies
using rigorous statistical methods.
"""


def test_topic_hierarchy():
    """Test the new hierarchical topic detection"""

    print("="*80)
    print("TESTING NEW HIERARCHICAL TOPIC DETECTION")
    print("="*80)
    print("\nJob Description:")
    print(SAMPLE_JOB_DESCRIPTION)
    print("\n" + "="*80)

    # Analyze the job description
    result = learning_path_service.analyze_job_description(SAMPLE_JOB_DESCRIPTION)

    # Print the full result as JSON for inspection
    print("\n" + "="*80)
    print("FULL JSON RESULT:")
    print("="*80)
    print(json.dumps(result, indent=2))
    print("="*80)

    # Validate structure
    print("\n" + "="*80)
    print("VALIDATION CHECKS:")
    print("="*80)

    topic_hierarchy = result.get('topic_hierarchy', {})
    explicit_topics = topic_hierarchy.get('explicit_topics', [])
    implicit_topics = topic_hierarchy.get('implicit_topics', [])

    # Check 1: Explicit topics have required fields
    print("\n✓ Checking explicit topics structure...")
    for i, topic in enumerate(explicit_topics, 1):
        required_fields = ['name', 'priority', 'keywords', 'mentioned_explicitly', 'context']
        missing_fields = [f for f in required_fields if f not in topic]

        if missing_fields:
            print(f"  ❌ Topic {i} missing fields: {missing_fields}")
        else:
            print(f"  ✅ Topic {i} ({topic['name']}): all fields present")
            print(f"     Priority: {topic['priority']}, Keywords: {len(topic['keywords'])}")

    # Check 2: Implicit topics have required fields
    print("\n✓ Checking implicit topics structure...")
    for i, topic in enumerate(implicit_topics, 1):
        required_fields = ['name', 'priority', 'keywords', 'mentioned_explicitly', 'reason']
        missing_fields = [f for f in required_fields if f not in topic]

        if missing_fields:
            print(f"  ❌ Topic {i} missing fields: {missing_fields}")
        else:
            print(f"  ✅ Topic {i} ({topic['name']}): all fields present")
            print(f"     Priority: {topic['priority']}, Reason: {topic['reason'][:50]}...")

    # Check 3: Verify expected topics are detected
    print("\n✓ Checking expected topics are detected...")
    expected_explicit = [
        "statistical modeling",
        "time series",
        "machine learning",
        "python",
        "portfolio optimization",
        "backtesting"
    ]

    detected_explicit = [t['name'].lower() for t in explicit_topics]

    for expected in expected_explicit:
        found = any(expected in detected.lower() for detected in detected_explicit)
        status = "✅" if found else "⚠️"
        print(f"  {status} '{expected}': {'FOUND' if found else 'NOT FOUND'}")

    # Check 4: Verify priorities are assigned correctly
    print("\n✓ Checking priority distribution...")
    high_count = sum(1 for t in explicit_topics if t['priority'] == 'HIGH')
    medium_count = sum(1 for t in explicit_topics if t['priority'] == 'MEDIUM')
    low_count = sum(1 for t in explicit_topics if t['priority'] == 'LOW')

    print(f"  Explicit topics - HIGH: {high_count}, MEDIUM: {medium_count}, LOW: {low_count}")

    high_count = sum(1 for t in implicit_topics if t['priority'] == 'HIGH')
    medium_count = sum(1 for t in implicit_topics if t['priority'] == 'MEDIUM')
    low_count = sum(1 for t in implicit_topics if t['priority'] == 'LOW')

    print(f"  Implicit topics - HIGH: {high_count}, MEDIUM: {medium_count}, LOW: {low_count}")

    # Check 5: Verify keywords are provided
    print("\n✓ Checking keywords...")
    topics_with_keywords = sum(1 for t in explicit_topics + implicit_topics if len(t.get('keywords', [])) > 0)
    total_topics = len(explicit_topics) + len(implicit_topics)

    print(f"  Topics with keywords: {topics_with_keywords}/{total_topics}")
    if topics_with_keywords == total_topics:
        print("  ✅ All topics have keywords")
    else:
        print(f"  ⚠️ {total_topics - topics_with_keywords} topics missing keywords")

    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)


if __name__ == "__main__":
    test_topic_hierarchy()
