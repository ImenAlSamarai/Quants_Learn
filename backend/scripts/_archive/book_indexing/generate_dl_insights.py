"""
Generate practitioner insights for ALL Deep Learning topics

Extracts bibliographic notes and discussion from chapters, then uses LLM to structure
into actionable interview-relevant insights.

Topics covered:
- Chapters 7-8: Training (4 topics)
- Chapter 6: Fundamentals (4 topics)
- Chapter 10: CNNs (4 topics)
- Chapter 12: Transformers (4 topics)

Total: 16 topics
"""

import os
import sys
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.database import SessionLocal, Node, TopicInsights, init_db
from app.services.llm_service import LLMService
from dl_book_extractor import DeepLearningBookExtractor
import re
import json


class DLInsightsGenerator:
    """Generate structured insights from Deep Learning book content"""

    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.db = SessionLocal()
        self.extractor = DeepLearningBookExtractor(pdf_path)
        self.llm = LLMService()

    def extract_chapter_discussion(self, chapter_num: int) -> str:
        """
        Extract discussion sections from chapter

        Deep Learning book has end-of-chapter material including
        exercises and discussions. Extract these for context.
        """
        chapter_data = self.extractor.extract_chapter(chapter_num)
        if not chapter_data:
            return ""

        text = chapter_data['text']
        lines = text.split('\n')

        # Try to find "Exercises", "Further Reading", "Summary" sections
        discussion_start = None
        for i, line in enumerate(lines):
            if re.match(r'^(Exercises?|Further Reading|Summary|Bibliographic|Discussion)', line.strip(), re.IGNORECASE):
                discussion_start = i
                break

        if discussion_start is None:
            # Use last 20% of chapter as context
            discussion_start = int(len(lines) * 0.8)

        content = '\n'.join(lines[discussion_start:])
        return content.strip()

    def generate_structured_insights(self, raw_text: str, topic_title: str, chapter_content: str) -> dict:
        """Use LLM to structure raw discussion text into actionable insights"""

        prompt = f"""
You are analyzing practitioner insights from "Deep Learning: Foundations and Concepts" about {topic_title}.

Extract and organize the following information from the chapter content and discussion:

1. **When to Use** - Scenarios where this method/technique is appropriate vs alternatives
   Format: [{{"scenario": "description", "rationale": "why it works well here"}}]

2. **Limitations & Caveats** - Key limitations practitioners should know
   Format: [{{"issue": "the limitation", "explanation": "why it matters", "mitigation": "how to address it (if applicable)"}}]

3. **Practical Tips** - Implementation advice and best practices
   Format: ["tip 1", "tip 2", ...]

4. **Method Comparisons** - How it compares to related methods
   Format: [{{"method_a": "this method", "method_b": "alternative", "key_difference": "main distinction", "when_to_prefer": "guidance"}}]

5. **Computational Notes** - Complexity, scalability, implementation notes
   Format: Simple text paragraph

Source text:
{raw_text}

Additional chapter context:
{chapter_content[:2000]}

Return ONLY valid JSON in this exact format:
{{
  "when_to_use": [...],
  "limitations": [...],
  "practical_tips": [...],
  "method_comparisons": [...],
  "computational_notes": "..."
}}

Be specific and interview-relevant for quantitative finance roles. Focus on practical knowledge that shows depth.
"""

        try:
            response = self.llm.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are a quantitative researcher extracting practical insights from technical content. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )

            content = response.choices[0].message.content
            insights = json.loads(content)

            required_keys = ['when_to_use', 'limitations', 'practical_tips', 'method_comparisons', 'computational_notes']
            for key in required_keys:
                if key not in insights:
                    insights[key] = [] if key != 'computational_notes' else ""

            return insights

        except Exception as e:
            print(f"  Error generating insights: {e}")
            return {
                'when_to_use': [],
                'limitations': [],
                'practical_tips': [],
                'method_comparisons': [],
                'computational_notes': ""
            }

    def generate_insights_for_topic(self, node: Node, chapter_num: int):
        """Generate and save insights for a specific topic"""

        print(f"\nGenerating insights for: {node.title}")

        # Get chapter discussion/end matter
        discussion = self.extract_chapter_discussion(chapter_num)

        # Also get full chapter for context
        chapter_data = self.extractor.extract_chapter(chapter_num)
        chapter_context = chapter_data['text'] if chapter_data else ""

        if not discussion or len(discussion) < 100:
            print(f"  Using full chapter context for {node.title}")
            discussion = chapter_context[:3000]  # Use first part of chapter

        print(f"  Extracted {len(discussion)} characters of discussion/context")
        print(f"  Generating structured insights with LLM...")
        insights_data = self.generate_structured_insights(discussion, node.title, chapter_context)

        existing = self.db.query(TopicInsights).filter(TopicInsights.node_id == node.id).first()

        if existing:
            print(f"  Updating existing insights")
            existing.when_to_use = insights_data['when_to_use']
            existing.limitations = insights_data['limitations']
            existing.practical_tips = insights_data['practical_tips']
            existing.method_comparisons = insights_data['method_comparisons']
            existing.computational_notes = insights_data['computational_notes']
            existing.bibliographic_notes = discussion
        else:
            print(f"  Creating new insights")
            topic_insights = TopicInsights(
                node_id=node.id,
                when_to_use=insights_data['when_to_use'],
                limitations=insights_data['limitations'],
                practical_tips=insights_data['practical_tips'],
                method_comparisons=insights_data['method_comparisons'],
                computational_notes=insights_data['computational_notes'],
                bibliographic_notes=discussion,
                discussion_sections=[]
            )
            self.db.add(topic_insights)

        self.db.commit()
        print(f"  ✓ Insights saved")
        print(f"    - When to use: {len(insights_data['when_to_use'])} scenarios")
        print(f"    - Limitations: {len(insights_data['limitations'])} items")
        print(f"    - Practical tips: {len(insights_data['practical_tips'])} tips")
        print(f"    - Comparisons: {len(insights_data['method_comparisons'])} comparisons")

    def close(self):
        self.db.close()
        self.extractor.close()


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Generate insights for Deep Learning topics")
    parser.add_argument('--init-db', action='store_true', help='Initialize database')
    parser.add_argument('--pdf-path', default='../content/machine_learning/deep_learning_foundations_and_concepts.pdf')
    args = parser.parse_args()

    if args.init_db:
        print("Initializing database...")
        init_db()
        print()

    generator = DLInsightsGenerator(args.pdf_path)

    print("=" * 80)
    print("Deep Learning Topics Insights Generation")
    print("=" * 80)
    print()

    # Define all DL topics and their source chapters
    dl_topics = [
        # Chapters 7-8: Training
        ("Gradient Descent and Optimization", 7),
        ("Backpropagation Algorithm", 8),
        ("Advanced Optimizers (Adam, RMSprop, Momentum)", 7),
        ("Batch Normalization and Layer Normalization", 8),

        # Chapter 6: Fundamentals
        ("Feedforward Neural Networks", 6),
        ("Activation Functions", 6),
        ("Output Units and Loss Functions", 6),
        ("Universal Approximation", 6),

        # Chapter 10: CNNs
        ("Convolutional Neural Networks (CNNs)", 10),
        ("Pooling and Subsampling", 10),
        ("CNN Architectures (LeNet, AlexNet, VGG, ResNet)", 10),
        ("Transfer Learning and Fine-Tuning", 10),

        # Chapter 12: Transformers
        ("Attention Mechanisms", 12),
        ("Self-Attention and Multi-Head Attention", 12),
        ("Transformer Architecture", 12),
        ("Transformer Language Models (BERT, GPT)", 12),
    ]

    db = SessionLocal()

    try:
        for i, (topic_title, chapter_num) in enumerate(dl_topics, 1):
            print(f"\n[{i}/{len(dl_topics)}] Processing: {topic_title}")

            node = db.query(Node).filter(Node.title == topic_title).first()

            if not node:
                print(f"  ⚠️  Topic not found in database: {topic_title}")
                print(f"  Skipping...")
                continue

            generator.generate_insights_for_topic(node, chapter_num)

        print("\n" + "=" * 80)
        print("✓ Deep Learning insights generation completed!")
        print("=" * 80)
        print(f"\nProcessed {len(dl_topics)} topics")
        print("\nNext steps:")
        print("  1. Start backend: uvicorn app.main:app --reload")
        print("  2. Start frontend: npm run dev")
        print("  3. Test insights button on DL topics!")

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

    finally:
        db.close()
        generator.close()


if __name__ == "__main__":
    main()
