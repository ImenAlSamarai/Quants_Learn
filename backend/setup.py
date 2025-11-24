#!/usr/bin/env python3
"""
Quant Learning Platform - Professional Setup & Verification Tool

This script provides a complete setup and verification pipeline for the platform.
It checks all prerequisites, verifies data integrity, and offers to fix issues.

Usage:
    python setup.py                    # Run full verification
    python setup.py --check-only       # Only check, don't offer fixes
    python setup.py --setup-all        # Run full setup (non-interactive)
    python setup.py --status           # Quick status overview
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Tuple
import argparse
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from setup.checks.database import DatabaseChecker
from setup.checks.content import ContentChecker
from setup.checks.insights import InsightsChecker

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class SetupOrchestrator:
    """Main setup and verification orchestrator"""

    def __init__(self, interactive: bool = True):
        self.interactive = interactive
        self.results = {}
        self.issues = []
        self.warnings = []

    def print_header(self, text: str):
        """Print section header"""
        print(f"\n{Colors.BOLD}{Colors.HEADER}{'=' * 80}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.HEADER}{text}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.HEADER}{'=' * 80}{Colors.ENDC}\n")

    def print_status(self, status: str, message: str):
        """Print status message"""
        if status == 'ok':
            symbol = f"{Colors.OKGREEN}✓{Colors.ENDC}"
        elif status == 'warning':
            symbol = f"{Colors.WARNING}⚠{Colors.ENDC}"
        elif status == 'error' or status == 'missing':
            symbol = f"{Colors.FAIL}✗{Colors.ENDC}"
        else:
            symbol = "•"

        print(f"  {symbol} {message}")

    def check_prerequisites(self) -> bool:
        """Check environment prerequisites"""
        self.print_header("1. Checking Prerequisites")

        all_ok = True

        # Check Python version
        python_version = sys.version_info
        if python_version.major >= 3 and python_version.minor >= 9:
            self.print_status('ok', f"Python {python_version.major}.{python_version.minor} ✓")
        else:
            self.print_status('error', f"Python {python_version.major}.{python_version.minor} (3.9+ required)")
            all_ok = False

        # Check .env file
        env_file = Path(__file__).parent / '.env'
        if env_file.exists():
            self.print_status('ok', ".env configuration file exists")

            # Check critical env vars
            from dotenv import load_dotenv
            load_dotenv()

            critical_vars = ['DATABASE_URL', 'OPENAI_API_KEY', 'PINECONE_API_KEY']
            for var in critical_vars:
                value = os.getenv(var)
                if value and value != f"your_{var.lower()}_here":
                    self.print_status('ok', f"{var} configured")
                else:
                    self.print_status('warning', f"{var} not configured")
                    self.warnings.append(f"Set {var} in .env file")
        else:
            self.print_status('warning', ".env file missing (copy from .env.example)")
            self.warnings.append("Create .env file from .env.example")

        # Check content files exist
        content_path = Path(__file__).parent.parent / 'content'
        if content_path.exists():
            self.print_status('ok', f"Content directory exists: {content_path}")

            # Check for PDF books
            books = {
                'ESL': content_path / 'machine_learning' / 'elements_of_statistical_learning.pdf',
                'DL': content_path / 'machine_learning' / 'deep_learning_foundations_and_concepts.pdf',
                'Bouchaud': content_path / 'statistics' / 'bouchaud_book.pdf'
            }

            for book_name, book_path in books.items():
                if book_path.exists():
                    size_mb = book_path.stat().st_size / (1024 * 1024)
                    self.print_status('ok', f"{book_name} book present ({size_mb:.1f} MB)")
                else:
                    self.print_status('warning', f"{book_name} book missing: {book_path}")
        else:
            self.print_status('error', "Content directory not found")
            all_ok = False

        return all_ok

    def check_database(self) -> bool:
        """Check database status"""
        self.print_header("2. Checking Database")

        checker = DatabaseChecker()
        result = checker.run_all_checks()

        for check_name, check_result in result['results'].items():
            status = check_result['status']
            message = check_result['message']

            self.print_status(status, message)

            if status == 'error' or status == 'missing':
                self.issues.append(('database', check_name, check_result))
            elif status == 'warning':
                self.warnings.append(message)

        # Print data counts if available
        if 'data_counts' in result['results']:
            counts = result['results']['data_counts'].get('counts', {})
            print(f"\n  {Colors.OKCYAN}Current Data:{Colors.ENDC}")
            print(f"    • Nodes: {counts.get('nodes', 0)}")
            print(f"    • Content Chunks: {counts.get('content_chunks', 0)}")
            print(f"    • Insights: {counts.get('insights', 0)}")
            print(f"    • Users: {counts.get('users', 0)}")

        self.results['database'] = result
        return result['passed']

    def check_content(self) -> bool:
        """Check content indexing status"""
        self.print_header("3. Checking Content Indexing")

        checker = ContentChecker()
        result = checker.run_all_checks()

        for check_name, check_result in result['results'].items():
            if check_name in ['nodes', 'content_chunks']:
                status = check_result['status']
                message = check_result['message']

                self.print_status(status, message)

                if status == 'error' or status == 'missing':
                    self.issues.append(('content', check_name, check_result))
                elif status == 'warning':
                    self.warnings.append(message)

        # Show book status
        if 'books' in result['results']:
            print(f"\n  {Colors.OKCYAN}Book Content Status:{Colors.ENDC}")
            for book_id, book_info in result['results']['books']['books'].items():
                status_symbol = "✓" if book_info['file_exists'] else "✗"
                indexed_info = ""
                if 'indexed_topics' in book_info:
                    indexed_info = f" ({len(book_info['indexed_topics'])}/{book_info['total_topics']} topics indexed)"

                print(f"    {status_symbol} {book_info['name']}: {book_info['expected_status']}{indexed_info}")

        self.results['content'] = result
        return result['passed']

    def check_insights(self) -> bool:
        """Check insights generation status"""
        self.print_header("4. Checking Insights")

        checker = InsightsChecker()
        result = checker.run_all_checks()

        if 'insights' in result['results']:
            status = result['results']['insights']['status']
            message = result['results']['insights']['message']

            self.print_status(status, message)

            if status == 'error' or status == 'missing':
                self.issues.append(('insights', 'generation', result['results']['insights']))
            elif status == 'warning':
                self.warnings.append(message)

        # Show book coverage
        if 'book_coverage' in result['results']:
            print(f"\n  {Colors.OKCYAN}Insights Coverage:{Colors.ENDC}")
            for book_id, coverage in result['results']['book_coverage']['coverage'].items():
                with_insights = len(coverage['chapters_with_insights'])
                missing_insights = len(coverage['chapters_missing_insights'])
                total = with_insights + missing_insights

                if total > 0:
                    percentage = (with_insights / total) * 100
                    print(f"    • {coverage['name']}: {with_insights}/{total} topics ({percentage:.0f}%)")

        self.results['insights'] = result
        return result['passed']

    def print_summary(self):
        """Print overall summary"""
        self.print_header("Summary")

        # Count issues
        critical_issues = len([i for i in self.issues if i[1] != 'warning'])
        warnings_count = len(self.warnings)

        if critical_issues == 0 and warnings_count == 0:
            print(f"{Colors.OKGREEN}{Colors.BOLD}✓ System is fully operational!{Colors.ENDC}\n")
            print("All checks passed. The platform is ready to use.")
            return True
        elif critical_issues == 0:
            print(f"{Colors.WARNING}{Colors.BOLD}⚠ System operational with warnings{Colors.ENDC}\n")
            print(f"Found {warnings_count} warning(s):\n")
            for i, warning in enumerate(self.warnings, 1):
                print(f"  {i}. {warning}")
            return True
        else:
            print(f"{Colors.FAIL}{Colors.BOLD}✗ Issues found that need attention{Colors.ENDC}\n")
            print(f"Critical issues: {critical_issues}")
            print(f"Warnings: {warnings_count}\n")

            # Group issues by category
            db_issues = [i for i in self.issues if i[0] == 'database']
            content_issues = [i for i in self.issues if i[0] == 'content']
            insights_issues = [i for i in self.issues if i[0] == 'insights']

            if db_issues:
                print(f"{Colors.FAIL}Database Issues:{Colors.ENDC}")
                for _, check_name, details in db_issues:
                    print(f"  • {check_name}: {details.get('message', 'Unknown error')}")
                print()

            if content_issues:
                print(f"{Colors.FAIL}Content Issues:{Colors.ENDC}")
                for _, check_name, details in content_issues:
                    print(f"  • {check_name}: {details.get('message', 'Unknown error')}")
                print()

            if insights_issues:
                print(f"{Colors.FAIL}Insights Issues:{Colors.ENDC}")
                for _, check_name, details in insights_issues:
                    print(f"  • {check_name}: {details.get('message', 'Unknown error')}")
                print()

            return False

    def offer_fixes(self):
        """Offer to fix found issues"""
        if not self.interactive:
            return

        if not self.issues:
            return

        print(f"\n{Colors.BOLD}Available Fixes:{Colors.ENDC}\n")

        fixes = []

        # Database fixes
        db_issues = [i for i in self.issues if i[0] == 'database']
        if db_issues:
            fixes.append(('init_db', "Initialize database tables", "python -c \"from app.models.database import init_db; init_db()\""))

        # Content fixes
        content_issues = [i for i in self.issues if i[0] == 'content']
        if content_issues:
            fixes.append(('index_content', "Index all content", "python scripts/index_content.py --init-db"))

        # Insights fixes
        insights_issues = [i for i in self.issues if i[0] == 'insights']
        if insights_issues:
            fixes.append(('generate_insights', "Generate insights for ESL topics", "python scripts/generate_all_insights.py"))

        for i, (fix_id, description, command) in enumerate(fixes, 1):
            print(f"  {i}. {description}")
            print(f"     Command: {Colors.OKCYAN}{command}{Colors.ENDC}")
            print()

        print(f"{Colors.WARNING}Note: Run these commands from the backend/ directory{Colors.ENDC}")

    def run_quick_status(self):
        """Run quick status check"""
        print(f"\n{Colors.BOLD}Quant Learning Platform - Quick Status{Colors.ENDC}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        try:
            db = DatabaseChecker()
            db_result = db.run_all_checks()

            if 'data_counts' in db_result['results']:
                counts = db_result['results']['data_counts']['counts']

                status = "🟢 READY" if counts.get('nodes', 0) > 0 else "🔴 NEEDS SETUP"

                print(f"Status: {status}\n")
                print(f"Nodes:          {counts.get('nodes', 0)}")
                print(f"Content Chunks: {counts.get('content_chunks', 0)}")
                print(f"Insights:       {counts.get('insights', 0)}")
                print(f"Users:          {counts.get('users', 0)}")
                print()

                if counts.get('nodes', 0) == 0:
                    print(f"{Colors.WARNING}→ Run: python setup.py  (for full setup){Colors.ENDC}")
            else:
                print(f"{Colors.FAIL}✗ Database not accessible{Colors.ENDC}")
                print(f"{Colors.WARNING}→ Check DATABASE_URL in .env{Colors.ENDC}")

        except Exception as e:
            print(f"{Colors.FAIL}✗ Error: {str(e)}{Colors.ENDC}")

    def run_full_check(self) -> bool:
        """Run all verification checks"""
        print(f"\n{Colors.BOLD}{Colors.OKBLUE}")
        print("╔══════════════════════════════════════════════════════════════════════════════╗")
        print("║                  Quant Learning Platform - Setup Verification                ║")
        print("╚══════════════════════════════════════════════════════════════════════════════╝")
        print(f"{Colors.ENDC}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        steps = [
            self.check_prerequisites,
            self.check_database,
            self.check_content,
            self.check_insights,
        ]

        all_passed = True
        for step in steps:
            try:
                if not step():
                    all_passed = False
            except Exception as e:
                print(f"{Colors.FAIL}Error during check: {str(e)}{Colors.ENDC}")
                all_passed = False

        summary_ok = self.print_summary()

        if not summary_ok and self.interactive:
            self.offer_fixes()

        return all_passed


def main():
    parser = argparse.ArgumentParser(
        description='Quant Learning Platform Setup & Verification',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--check-only',
        action='store_true',
        help='Only run checks, do not offer fixes'
    )

    parser.add_argument(
        '--status',
        action='store_true',
        help='Quick status overview only'
    )

    parser.add_argument(
        '--setup-all',
        action='store_true',
        help='Run full setup (non-interactive)'
    )

    args = parser.parse_args()

    orchestrator = SetupOrchestrator(interactive=not args.check_only)

    if args.status:
        orchestrator.run_quick_status()
    else:
        success = orchestrator.run_full_check()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
