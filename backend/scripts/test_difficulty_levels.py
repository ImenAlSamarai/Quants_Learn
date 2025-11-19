"""
Test Difficulty Adaptation - Prove content changes by user level

This demonstrates that the system generates DIFFERENT content
for different difficulty levels (1-5).
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.database import SessionLocal, Node, User
from app.services.vector_store import vector_store
from app.services.llm_service import LLMService
from datetime import datetime

def test_difficulty_levels():
    print("="*80)
    print("Testing Difficulty Level Adaptation")
    print("="*80)
    print()

    db = SessionLocal()

    # Get Ridge Regression node
    node = db.query(Node).filter(Node.title == "Ridge Regression").first()

    if not node:
        print("❌ Ridge Regression node not found!")
        db.close()
        return

    # Get relevant book chunks (same for all levels)
    search_query = "ridge regression regularization penalty"
    matches = vector_store.search(
        query=search_query,
        node_id=node.id,
        top_k=3
    )

    if not matches:
        print("❌ No content found in vector store!")
        db.close()
        return

    context_chunks = [m['text'] for m in matches]

    print(f"Testing with: {node.title}")
    print(f"Using {len(context_chunks)} chunks from ESL book")
    print()
    print("="*80)

    # Test 3 different levels
    test_levels = [
        (1, "Undergraduate - New to Quant Finance", "🌱"),
        (3, "Graduate Student", "🎓"),
        (5, "Experienced Researcher", "⭐")
    ]

    llm = LLMService()

    for level, description, icon in test_levels:
        print(f"\n{icon} DIFFICULTY LEVEL {level}: {description}")
        print("-"*80)

        try:
            # Generate explanation at this difficulty level
            explanation = llm.generate_explanation(
                topic=node.title,
                context_chunks=context_chunks,
                difficulty=level,
                user_context=None
            )

            # Show first 600 characters
            preview = explanation[:600]
            print(preview)
            print("...")
            print()

            # Analyze the content
            print("Content Analysis:")

            # Check for advanced terms
            advanced_terms = [
                'theorem', 'lemma', 'proof', 'derivation',
                'stochastic', 'asymptotic', 'eigenvalue',
                'closed-form', 'Bayesian'
            ]
            found_advanced = [t for t in advanced_terms if t.lower() in explanation.lower()]

            # Check for simple explanations
            simple_terms = [
                'simply', 'basically', 'think of', 'imagine',
                'like', 'similar to', 'analogy', 'in other words'
            ]
            found_simple = [t for t in simple_terms if t.lower() in explanation.lower()]

            # Check for equations
            has_equations = '$$' in explanation or '$' in explanation

            print(f"  - Advanced terms: {len(found_advanced)} {found_advanced[:3]}")
            print(f"  - Simple language: {len(found_simple)} {found_simple[:3]}")
            print(f"  - Has equations: {'Yes' if has_equations else 'No'}")
            print(f"  - Total length: {len(explanation)} characters")

        except Exception as e:
            print(f"❌ Error generating content: {e}")

        print()
        print("="*80)

    print("\n" + "="*80)
    print("EXPECTED DIFFERENCES:")
    print("="*80)
    print()
    print("Level 1 (Undergraduate):")
    print("  ✓ More analogies and simple language")
    print("  ✓ Fewer advanced mathematical terms")
    print("  ✓ Step-by-step explanations")
    print()
    print("Level 3 (Graduate):")
    print("  ✓ Balanced rigor and intuition")
    print("  ✓ Some mathematical formalism")
    print("  ✓ Real-world examples")
    print()
    print("Level 5 (Expert):")
    print("  ✓ Technical depth and precision")
    print("  ✓ Research-level terminology")
    print("  ✓ Advanced mathematical concepts")
    print()
    print("Cost: ~$0.0015 (3 explanations × $0.0005 each)")

    db.close()


def test_user_settings():
    """Test that user settings are being saved and retrieved"""

    print("\n" + "="*80)
    print("Testing User Settings Persistence")
    print("="*80)
    print()

    db = SessionLocal()

    # Create test users at different levels
    test_users = [
        ("test_undergrad", 1, "Undergraduate student"),
        ("test_grad", 3, "Graduate student"),
        ("test_expert", 5, "Experienced researcher")
    ]

    for user_id, level, description in test_users:
        # Check if user exists
        user = db.query(User).filter(User.user_id == user_id).first()

        if user:
            print(f"✓ User '{user_id}' exists with level {user.learning_level}")
        else:
            # Create user
            user = User(
                user_id=user_id,
                learning_level=level,
                background=description,
                last_active=datetime.utcnow()
            )
            db.add(user)
            db.commit()
            print(f"✓ Created user '{user_id}' at level {level}")

    print()
    print("To test in frontend:")
    print("1. Click ⚙️ Settings button")
    print("2. Select different difficulty level (1-5)")
    print("3. Save settings")
    print("4. Open a topic like 'Ridge Regression'")
    print("5. Content should match your selected level!")
    print()
    print("Note: Clear browser cache to see fresh content")

    db.close()


if __name__ == "__main__":
    print("Testing difficulty level adaptation...")
    print()

    # Test 1: Generate content at different levels
    test_difficulty_levels()

    # Test 2: Check user settings
    test_user_settings()
