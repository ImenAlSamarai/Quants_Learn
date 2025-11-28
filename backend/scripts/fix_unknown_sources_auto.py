#!/usr/bin/env python3
"""
Quick fix for Unknown sources - automatically update to correct book name

Usage:
    python scripts/fix_unknown_sources_auto.py
"""

import os
import sys
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.vector_store import vector_store
from app.models.database import SessionLocal, Node, ContentChunk


def fix_unknown_sources():
    """Automatically fix all Unknown sources"""

    print("\n" + "="*80)
    print("🔧 AUTO-FIXING 'Unknown' SOURCES")
    print("="*80 + "\n")

    # Get all nodes from database
    db = SessionLocal()
    all_chunks = db.query(ContentChunk).all()

    print(f"Found {len(all_chunks)} content chunks in database")

    # Query Pinecone for each chunk and check for Unknown
    unknown_count = 0
    fixed_count = 0

    for chunk in all_chunks:
        try:
            # Search Pinecone for this specific vector
            vector_id = chunk.vector_id

            # Fetch the vector from Pinecone
            fetch_result = vector_store.index.fetch(ids=[vector_id])

            if vector_id not in fetch_result['vectors']:
                continue

            vector_data = fetch_result['vectors'][vector_id]
            metadata = vector_data.get('metadata', {})
            source = metadata.get('source', 'Unknown')

            # Check if source is Unknown
            if source == 'Unknown' or 'Unknown' in source:
                unknown_count += 1

                # Determine correct source based on text content
                text = metadata.get('text', '')

                # Heuristics to identify the book
                correct_source = None
                chapter = metadata.get('chapter', 'N/A')

                # Check for probability brain teasers / interview questions
                if any(keyword in text.lower() for keyword in [
                    'probability', 'die', 'coin flip', 'bayes', 'conditional',
                    'interview', 'puzzle', 'brain teaser'
                ]):
                    if 'statistics matters' in text.lower() or 'why probability matters' in text.lower():
                        correct_source = 'Quant Interview Questions: Probability'

                # Check for Bouchaud content
                elif any(keyword in text.lower() for keyword in [
                    'lévy', 'levy', 'fat tail', 'heavy tail', 'pareto',
                    'power law', 'diverging moment', 'bouchaud'
                ]):
                    correct_source = f'Bouchaud: Theory of Financial Risk and Derivative Pricing, Chapter {chapter}'

                # Default: Keep as Unknown but log it
                else:
                    print(f"⚠️  Could not identify source for vector {vector_id}")
                    print(f"   Preview: {text[:100]}...")
                    continue

                # Update metadata
                metadata['source'] = correct_source

                # Re-upsert the vector with updated metadata
                vector_store.index.upsert(vectors=[{
                    'id': vector_id,
                    'values': vector_data['values'],
                    'metadata': metadata
                }])

                fixed_count += 1
                print(f"✓ Fixed: {vector_id}")
                print(f"  Old: Unknown")
                print(f"  New: {correct_source}")

        except Exception as e:
            print(f"❌ Error processing chunk {chunk.id}: {e}")
            continue

    db.close()

    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Total Unknown sources found: {unknown_count}")
    print(f"Successfully fixed: {fixed_count}")
    print(f"Unable to identify: {unknown_count - fixed_count}")
    print("="*80 + "\n")

    if fixed_count > 0:
        print("✅ Success! Re-run your job description test to see the correct book names.")
    else:
        print("⚠️  No Unknown sources were fixed. They may need manual identification.")


if __name__ == "__main__":
    fix_unknown_sources()
