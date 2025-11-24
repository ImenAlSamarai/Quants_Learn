"""
Database verification checks
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import inspect, text
from app.models.database import engine, Node, TopicInsights, ContentChunk, User, UserProgress, GeneratedContent


class DatabaseChecker:
    """Check database schema and connectivity"""

    def __init__(self):
        self.results = {}

    def check_connection(self) -> bool:
        """Verify database connection"""
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            self.results['connection'] = {'status': 'ok', 'message': 'Database connection successful'}
            return True
        except Exception as e:
            self.results['connection'] = {'status': 'error', 'message': f'Connection failed: {str(e)}'}
            return False

    def check_tables(self) -> bool:
        """Verify all required tables exist"""
        inspector = inspect(engine)
        existing_tables = set(inspector.get_table_names())

        required_tables = {
            'nodes': Node,
            'content_chunks': ContentChunk,
            'topic_insights': TopicInsights,
            'users': User,
            'user_progress': UserProgress,
            'generated_content': GeneratedContent,
            'node_edges': None  # Association table
        }

        missing_tables = []
        for table_name in required_tables.keys():
            if table_name not in existing_tables:
                missing_tables.append(table_name)

        if missing_tables:
            self.results['tables'] = {
                'status': 'missing',
                'message': f'Missing tables: {", ".join(missing_tables)}',
                'missing': missing_tables
            }
            return False
        else:
            self.results['tables'] = {
                'status': 'ok',
                'message': f'All {len(required_tables)} required tables exist',
                'tables': list(required_tables.keys())
            }
            return True

    def check_table_schemas(self) -> bool:
        """Verify table schemas have expected columns"""
        inspector = inspect(engine)

        critical_columns = {
            'nodes': ['id', 'title', 'slug', 'category', 'extra_metadata'],
            'topic_insights': ['id', 'node_id', 'when_to_use', 'limitations', 'practical_tips'],
            'content_chunks': ['id', 'node_id', 'chunk_text', 'vector_id']
        }

        issues = []
        for table, expected_cols in critical_columns.items():
            try:
                columns = [col['name'] for col in inspector.get_columns(table)]
                missing = set(expected_cols) - set(columns)
                if missing:
                    issues.append(f"{table}: missing columns {missing}")
            except Exception as e:
                issues.append(f"{table}: {str(e)}")

        if issues:
            self.results['schema'] = {
                'status': 'error',
                'message': 'Schema issues found',
                'issues': issues
            }
            return False
        else:
            self.results['schema'] = {
                'status': 'ok',
                'message': 'All table schemas valid'
            }
            return True

    def get_data_counts(self) -> dict:
        """Get counts of data in key tables"""
        from app.models.database import SessionLocal

        db = SessionLocal()
        try:
            counts = {
                'nodes': db.query(Node).count(),
                'insights': db.query(TopicInsights).count(),
                'content_chunks': db.query(ContentChunk).count(),
                'users': db.query(User).count(),
            }
            self.results['data_counts'] = {
                'status': 'ok',
                'counts': counts
            }
            return counts
        finally:
            db.close()

    def run_all_checks(self) -> dict:
        """Run all database checks"""
        checks = [
            ('connection', self.check_connection),
            ('tables', self.check_tables),
            ('schema', self.check_table_schemas),
        ]

        all_passed = True
        for check_name, check_func in checks:
            if not check_func():
                all_passed = False

        # Get data counts regardless of other checks
        try:
            self.get_data_counts()
        except:
            pass

        return {
            'passed': all_passed,
            'results': self.results
        }
