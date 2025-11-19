"""
Simple database check - no API keys required

Just checks what nodes and chunks exist in the database
"""

import sqlite3
import os

# Find the database file
db_paths = [
    "../quant_learn.db",
    "./quant_learn.db",
    "../../quant_learn.db"
]

db_path = None
for path in db_paths:
    if os.path.exists(path):
        db_path = path
        break

if not db_path:
    print("❌ Database file not found!")
    print("Expected locations:")
    for path in db_paths:
        print(f"  - {path}")
    print("\nDid you run: python scripts/index_esl_chapter3.py ?")
    exit(1)

print("="*80)
print("Simple Database Check (No API Keys Required)")
print("="*80)
print(f"Database: {db_path}")
print()

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check nodes
print("[1] Checking for Machine Learning nodes...")
print("-"*80)

cursor.execute("""
    SELECT id, title, category, subcategory, difficulty_level
    FROM nodes
    WHERE category = 'machine_learning'
    ORDER BY id
""")

ml_nodes = cursor.fetchall()

if not ml_nodes:
    print("❌ No Machine Learning nodes found!")
    print("\nYou need to run the indexing script:")
    print("  cd /Users/imenalsamarai/Documents/projects_MCP/Quants_Learn/backend")
    print("  python scripts/index_esl_chapter3.py")
else:
    print(f"✓ Found {len(ml_nodes)} Machine Learning nodes:")
    for node in ml_nodes:
        node_id, title, category, subcategory, difficulty = node
        print(f"  [{node_id}] {title}")
        print(f"      Category: {category}/{subcategory}, Difficulty: {difficulty}")

print()

# Check content chunks
print("[2] Checking content chunks...")
print("-"*80)

if ml_nodes:
    for node in ml_nodes:
        node_id = node[0]
        title = node[1]

        cursor.execute("""
            SELECT COUNT(*), SUM(LENGTH(chunk_text))
            FROM content_chunks
            WHERE node_id = ?
        """, (node_id,))

        count, total_chars = cursor.fetchone()

        if count:
            print(f"✓ {title}: {count} chunks, {total_chars:,} chars")

            # Show sample from first chunk
            cursor.execute("""
                SELECT chunk_text
                FROM content_chunks
                WHERE node_id = ?
                ORDER BY chunk_index
                LIMIT 1
            """, (node_id,))

            sample_chunk = cursor.fetchone()
            if sample_chunk:
                sample = sample_chunk[0][:200].replace('\n', ' ')
                print(f"  Sample: {sample}...")
        else:
            print(f"❌ {title}: No chunks found")
        print()

# Summary
print("="*80)
print("Summary")
print("="*80)

total_chunks = cursor.execute("SELECT COUNT(*) FROM content_chunks").fetchone()[0]
total_nodes = cursor.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]

print(f"Total nodes in database: {total_nodes}")
print(f"Total content chunks: {total_chunks}")

if ml_nodes:
    print(f"\n✓ Machine Learning topics: {len(ml_nodes)}")
    print("\n🎉 Chapter 3 content is indexed!")
    print("\nTo test RAG retrieval (requires API keys):")
    print("  1. Make sure backend/.env has OPENAI_API_KEY and PINECONE_API_KEY")
    print("  2. cd /Users/imenalsamarai/Documents/projects_MCP/Quants_Learn/backend")
    print("  3. python scripts/test_api_query.py")
else:
    print("\n⚠️  No Machine Learning nodes found.")
    print("\nRun indexing first:")
    print("  cd /Users/imenalsamarai/Documents/projects_MCP/Quants_Learn/backend")
    print("  python scripts/index_esl_chapter3.py")

conn.close()
