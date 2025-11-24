"""
Insights verification checks
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.models.database import SessionLocal, Node, TopicInsights
import yaml


class InsightsChecker:
    """Check if insights are generated for appropriate topics"""

    def __init__(self, config_path: str = None):
        self.results = {}
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "content_sources.yaml"

        with open(config_path) as f:
            self.config = yaml.safe_load(f)

    def check_insights_exist(self) -> bool:
        """Check if any insights exist"""
        db = SessionLocal()
        try:
            insight_count = db.query(TopicInsights).count()
            expected_min = self.config.get('expected_counts', {}).get('insights', 20)

            if insight_count == 0:
                self.results['insights'] = {
                    'status': 'missing',
                    'message': 'No insights in database',
                    'count': 0,
                    'expected': expected_min
                }
                return False
            elif insight_count < expected_min:
                self.results['insights'] = {
                    'status': 'warning',
                    'message': f'Only {insight_count} insights, expected {expected_min}',
                    'count': insight_count,
                    'expected': expected_min
                }
                return True
            else:
                self.results['insights'] = {
                    'status': 'ok',
                    'message': f'{insight_count} insights generated',
                    'count': insight_count
                }
                return True
        finally:
            db.close()

    def check_book_insights_coverage(self) -> dict:
        """Check which books have insights generated"""
        db = SessionLocal()
        try:
            coverage = {}

            for book_id, book_info in self.config.get('books', {}).items():
                if not book_info.get('requires_insights', False):
                    continue

                book_coverage = {
                    'name': book_info['name'],
                    'chapters_with_insights': [],
                    'chapters_missing_insights': []
                }

                if 'chapters' in book_info:
                    for chapter in book_info['chapters']:
                        chapter_num = chapter['number']
                        chapter_title = chapter['title']

                        # Check if topics from this chapter have insights
                        if 'topics' in chapter:
                            for topic_title in chapter['topics']:
                                node = db.query(Node).filter(
                                    Node.title.ilike(f'%{topic_title}%')
                                ).first()

                                if node:
                                    has_insight = db.query(TopicInsights).filter(
                                        TopicInsights.node_id == node.id
                                    ).first() is not None

                                    info = {
                                        'chapter': chapter_num,
                                        'title': chapter_title,
                                        'topic': topic_title,
                                        'node_id': node.id
                                    }

                                    if has_insight:
                                        book_coverage['chapters_with_insights'].append(info)
                                    else:
                                        book_coverage['chapters_missing_insights'].append(info)

                coverage[book_id] = book_coverage

            self.results['book_coverage'] = {
                'status': 'ok',
                'coverage': coverage
            }
            return coverage
        finally:
            db.close()

    def get_insights_details(self) -> list:
        """Get detailed list of all insights"""
        db = SessionLocal()
        try:
            insights_list = []

            insights = db.query(TopicInsights, Node).join(Node).all()
            for insight, node in insights:
                num_tips = len(insight.practical_tips) if insight.practical_tips else 0
                num_limitations = len(insight.limitations) if insight.limitations else 0
                num_comparisons = len(insight.method_comparisons) if insight.method_comparisons else 0
                num_when_to_use = len(insight.when_to_use) if insight.when_to_use else 0

                insights_list.append({
                    'node_id': node.id,
                    'title': node.title,
                    'category': node.category,
                    'when_to_use_count': num_when_to_use,
                    'limitations_count': num_limitations,
                    'tips_count': num_tips,
                    'comparisons_count': num_comparisons
                })

            self.results['insights_details'] = {
                'status': 'ok',
                'insights': insights_list
            }
            return insights_list
        finally:
            db.close()

    def run_all_checks(self) -> dict:
        """Run all insights checks"""
        passed = self.check_insights_exist()

        # These are informational
        self.check_book_insights_coverage()
        self.get_insights_details()

        return {
            'passed': passed,
            'results': self.results
        }
