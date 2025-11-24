"""
Content verification checks
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.models.database import SessionLocal, Node, ContentChunk
import yaml


class ContentChecker:
    """Check if content is properly indexed"""

    def __init__(self, config_path: str = None):
        self.results = {}
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "content_sources.yaml"

        with open(config_path) as f:
            self.config = yaml.safe_load(f)

    def check_nodes_exist(self) -> bool:
        """Verify nodes are created in database"""
        db = SessionLocal()
        try:
            node_count = db.query(Node).count()
            expected_min = self.config.get('expected_counts', {}).get('nodes', 20)

            if node_count == 0:
                self.results['nodes'] = {
                    'status': 'missing',
                    'message': 'No nodes in database',
                    'count': 0,
                    'expected_min': expected_min
                }
                return False
            elif node_count < expected_min:
                self.results['nodes'] = {
                    'status': 'warning',
                    'message': f'Only {node_count} nodes, expected at least {expected_min}',
                    'count': node_count,
                    'expected_min': expected_min
                }
                return True  # Not critical
            else:
                self.results['nodes'] = {
                    'status': 'ok',
                    'message': f'{node_count} nodes indexed',
                    'count': node_count
                }
                return True
        finally:
            db.close()

    def check_content_chunks(self) -> bool:
        """Verify content is chunked and stored"""
        db = SessionLocal()
        try:
            chunk_count = db.query(ContentChunk).count()
            expected_min = self.config.get('expected_counts', {}).get('content_chunks_min', 100)

            # Get chunks per category
            category_counts = {}
            nodes = db.query(Node).all()
            for node in nodes:
                cat = node.category
                chunk_count_for_node = db.query(ContentChunk).filter(
                    ContentChunk.node_id == node.id
                ).count()
                category_counts[cat] = category_counts.get(cat, 0) + chunk_count_for_node

            if chunk_count == 0:
                self.results['content_chunks'] = {
                    'status': 'missing',
                    'message': 'No content chunks in database - content not indexed',
                    'count': 0,
                    'expected_min': expected_min
                }
                return False
            elif chunk_count < expected_min:
                self.results['content_chunks'] = {
                    'status': 'warning',
                    'message': f'Only {chunk_count} chunks, expected at least {expected_min}',
                    'count': chunk_count,
                    'expected_min': expected_min,
                    'by_category': category_counts
                }
                return True
            else:
                self.results['content_chunks'] = {
                    'status': 'ok',
                    'message': f'{chunk_count} content chunks indexed',
                    'count': chunk_count,
                    'by_category': category_counts
                }
                return True
        finally:
            db.close()

    def check_book_content_status(self) -> dict:
        """Check status of each book's content"""
        db = SessionLocal()
        try:
            book_status = {}

            for book_id, book_info in self.config.get('books', {}).items():
                book_path = Path(book_info['path'])

                status = {
                    'name': book_info['name'],
                    'path': str(book_path),
                    'file_exists': book_path.exists(),
                    'expected_status': book_info.get('status', 'unknown'),
                    'category': book_info['category']
                }

                if book_path.exists():
                    # Check if content from this book is indexed
                    # We can infer this by checking if topics from chapters exist
                    if 'chapters' in book_info:
                        indexed_topics = []
                        for chapter in book_info['chapters']:
                            if 'topics' in chapter:
                                for topic_title in chapter['topics']:
                                    node = db.query(Node).filter(
                                        Node.title.ilike(f'%{topic_title}%')
                                    ).first()
                                    if node:
                                        indexed_topics.append(topic_title)

                        status['indexed_topics'] = indexed_topics
                        status['total_topics'] = sum(
                            len(ch.get('topics', [])) for ch in book_info['chapters']
                        )

                book_status[book_id] = status

            self.results['books'] = {
                'status': 'ok',
                'books': book_status
            }
            return book_status
        finally:
            db.close()

    def check_markdown_content_status(self) -> dict:
        """Check status of markdown content files"""
        markdown_status = {}

        for content_id, content_info in self.config.get('markdown_content', {}).items():
            category_status = {
                'category': content_info['category'],
                'expected_status': content_info.get('status', 'unknown'),
                'files': []
            }

            for file_path_str in content_info.get('files', []):
                file_path = Path(file_path_str)
                category_status['files'].append({
                    'path': str(file_path),
                    'exists': file_path.exists()
                })

            markdown_status[content_id] = category_status

        self.results['markdown_content'] = {
            'status': 'ok',
            'content': markdown_status
        }
        return markdown_status

    def run_all_checks(self) -> dict:
        """Run all content checks"""
        checks = [
            ('nodes', self.check_nodes_exist),
            ('chunks', self.check_content_chunks),
        ]

        all_passed = True
        for check_name, check_func in checks:
            if not check_func():
                all_passed = False

        # These are informational, don't affect pass/fail
        self.check_book_content_status()
        self.check_markdown_content_status()

        return {
            'passed': all_passed,
            'results': self.results
        }
