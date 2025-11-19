"""
Extract and generate practitioner insights for Chapter 7 topics (Model Assessment)
"""

import os
import sys
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.database import SessionLocal, Node, TopicInsights, init_db
from app.services.llm_service import LLMService
from pdf_extractor import ESLBookExtractor
import re
import json


class InsightsGenerator:
    """Generate structured insights from ESL book content"""

    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.db = SessionLocal()
        self.extractor = ESLBookExtractor(pdf_path)
        self.llm = LLMService()

    def extract_bibliographic_notes(self, chapter_num: int) -> str:
        """Extract bibliographic notes section from chapter"""
        chapter_data = self.extractor.extract_chapter(chapter_num)
        if not chapter_data:
            return ""

        text = chapter_data['text']
        lines = text.split('\n')

        start_idx = None
        for i, line in enumerate(lines):
            if re.match(r'^Bibliographic\s+Notes?', line.strip(), re.IGNORECASE):
                start_idx = i
                break

        if start_idx is None:
            print(f"  No bibliographic notes found in Chapter {chapter_num}")
            return ""

        end_idx = len(lines)
        for i in range(start_idx + 1, len(lines)):
            if re.match(r'^(Exercises?|References?|Chapter\s+\d+)', lines[i].strip(), re.IGNORECASE):
                end_idx = i
                break

        content = '\n'.join(lines[start_idx:end_idx])
        return content.strip()

    def generate_structured_insights(self, raw_text: str, topic_title: str) -> dict:
        """Use LLM to structure raw discussion text into actionable insights"""

        prompt = f"""
You are analyzing practitioner insights from "Elements of Statistical Learning" about {topic_title}.

Extract and organize the following information from the bibliographic notes and discussion:

1. **When to Use** - Scenarios where this method is appropriate vs alternatives
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

Return ONLY valid JSON in this exact format:
{{
  "when_to_use": [...],
  "limitations": [...],
  "practical_tips": [...],
  "method_comparisons": [...],
  "computational_notes": "..."
}}

Be specific and interview-relevant. Focus on practical knowledge that shows depth.
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

        biblio_notes = self.extract_bibliographic_notes(chapter_num)

        if not biblio_notes or len(biblio_notes) < 100:
            print(f"  Insufficient bibliographic content for {node.title}")
            return

        print(f"  Extracted {len(biblio_notes)} characters of bibliographic notes")
        print(f"  Generating structured insights with LLM...")
        insights_data = self.generate_structured_insights(biblio_notes, node.title)

        existing = self.db.query(TopicInsights).filter(TopicInsights.node_id == node.id).first()

        if existing:
            print(f"  Updating existing insights")
            existing.when_to_use = insights_data['when_to_use']
            existing.limitations = insights_data['limitations']
            existing.practical_tips = insights_data['practical_tips']
            existing.method_comparisons = insights_data['method_comparisons']
            existing.computational_notes = insights_data['computational_notes']
            existing.bibliographic_notes = biblio_notes
        else:
            print(f"  Creating new insights")
            topic_insights = TopicInsights(
                node_id=node.id,
                when_to_use=insights_data['when_to_use'],
                limitations=insights_data['limitations'],
                practical_tips=insights_data['practical_tips'],
                method_comparisons=insights_data['method_comparisons'],
                computational_notes=insights_data['computational_notes'],
                bibliographic_notes=biblio_notes,
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

    parser = argparse.ArgumentParser(description="Generate insights for Chapter 7 topics")
    parser.add_argument('--init-db', action='store_true', help='Initialize database')
    parser.add_argument('--pdf-path', default='../content/machine_learning/elements_of_statistical_learning.pdf')
    args = parser.parse_args()

    if args.init_db:
        print("Initializing database...")
        init_db()
        print()

    generator = InsightsGenerator(args.pdf_path)

    print("=" * 80)
    print("Chapter 7 Insights Generation: Model Assessment and Selection")
    print("=" * 80)

    chapter_7_topics = [
        "Bias-Variance Decomposition",
        "Cross-Validation Methods",
        "Bootstrap Methods",
        "Model Selection Criteria"
    ]

    db = SessionLocal()

    try:
        for topic_title in chapter_7_topics:
            node = db.query(Node).filter(Node.title == topic_title).first()

            if not node:
                print(f"\n⚠️  Topic not found: {topic_title}")
                continue

            generator.generate_insights_for_topic(node, chapter_num=7)

        print("\n" + "=" * 80)
        print("✓ Chapter 7 insights generation completed!")

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

    finally:
        db.close()
        generator.close()


if __name__ == "__main__":
    main()
