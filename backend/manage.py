#!/usr/bin/env python3
"""
Management CLI for Quants Learn Platform

Consolidates all operational scripts into single interface.

Usage:
    python manage.py health-check              # System diagnostics
    python manage.py update-content NODE_ID    # Update content + reindex
    python manage.py clear-cache [--node-id N] # Clear generated content cache
    python manage.py generate-insights [--category C] # Generate insights
"""

import sys
import argparse
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from management.commands.health_check import HealthCheckCommand
from management.commands.update_content import UpdateContentCommand
from management.commands.clear_cache import ClearCacheCommand
from management.commands.generate_insights import GenerateInsightsCommand
from management.commands.migrate_db import MigrateDatabaseCommand


def main():
    parser = argparse.ArgumentParser(
        description='Quants Learn Management CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python manage.py health-check
  python manage.py update-content --node-id 17
  python manage.py clear-cache --category statistics
  python manage.py generate-insights --all
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Health check command
    health_parser = subparsers.add_parser('health-check', help='Run system diagnostics')
    health_parser.add_argument('--verbose', action='store_true', help='Detailed output')

    # Update content command
    update_parser = subparsers.add_parser('update-content', help='Update and reindex content')
    update_parser.add_argument('--node-id', type=int, required=True, help='Node ID to update')
    update_parser.add_argument('--verify', action='store_true', help='Verify after update')

    # Clear cache command
    cache_parser = subparsers.add_parser('clear-cache', help='Clear generated content cache')
    cache_group = cache_parser.add_mutually_exclusive_group(required=True)
    cache_group.add_argument('--node-id', type=int, help='Clear cache for specific node')
    cache_group.add_argument('--category', type=str, help='Clear cache for category')
    cache_group.add_argument('--all', action='store_true', help='Clear all cache')
    cache_parser.add_argument('--inspect', action='store_true', help='Inspect cache without clearing')

    # Generate insights command
    insights_parser = subparsers.add_parser('generate-insights', help='Generate missing insights')
    insights_group = insights_parser.add_mutually_exclusive_group(required=True)
    insights_group.add_argument('--category', type=str, help='Generate for category')
    insights_group.add_argument('--all', action='store_true', help='Generate for all categories')

    # Database migration command
    migrate_parser = subparsers.add_parser('migrate-db', help='Migrate database to latest schema')
    migrate_parser.add_argument('--dry-run', action='store_true', help='Show migration plan without applying')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Route to appropriate command
    try:
        if args.command == 'health-check':
            cmd = HealthCheckCommand()
            return cmd.run(verbose=args.verbose)

        elif args.command == 'update-content':
            cmd = UpdateContentCommand()
            return cmd.run(node_id=args.node_id, verify=args.verify)

        elif args.command == 'clear-cache':
            cmd = ClearCacheCommand()
            if args.node_id:
                return cmd.run(node_id=args.node_id, inspect=args.inspect)
            elif args.category:
                return cmd.run(category=args.category)
            else:
                return cmd.run(clear_all=True)

        elif args.command == 'generate-insights':
            cmd = GenerateInsightsCommand()
            if args.category:
                return cmd.run(category=args.category)
            else:
                return cmd.run(all_categories=True)

        elif args.command == 'migrate-db':
            cmd = MigrateDatabaseCommand()
            return cmd.run(dry_run=args.dry_run)

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        return 130
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
