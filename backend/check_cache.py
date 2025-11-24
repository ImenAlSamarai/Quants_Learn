#!/usr/bin/env python3
"""Check cached content versions for node 17"""

import sys
sys.path.insert(0, '/home/user/Quants_Learn/backend')

from app.database import SessionLocal
from app.models.node import GeneratedContent

db = SessionLocal()
cached = db.query(GeneratedContent).filter(
    GeneratedContent.node_id == 17
).order_by(GeneratedContent.created_at).all()

print('\n📊 Cached content for node 17:\n')
print('Type            Difficulty   Version    Created')
print('-' * 60)
for c in cached:
    version = c.content_version if c.content_version is not None else 'None'
    print(f'{c.content_type:<15} {c.difficulty_level:<12} {version:<10} {str(c.created_at)[:19]}')

print(f'\nTotal cached entries: {len(cached)}')

# Check if there are any version 0 or None entries
old_cache = [c for c in cached if c.content_version is None or c.content_version == 0]
new_cache = [c for c in cached if c.content_version == 1]

print(f'\nVersion breakdown:')
print(f'  Version 0 or None: {len(old_cache)}')
print(f'  Version 1: {len(new_cache)}')

db.close()
