# Fixing "Unknown" Sources in Vector Store

## The Problem

When viewing learning path coverage, some topics show `Source: Unknown` instead of the actual book name. This happens when content was indexed without proper metadata.

**Example of the issue:**
```
✅ COVERED TOPICS (7):
  1. statistical modeling
     └─ Source: Unknown | Confidence: 54.9%
```

## Why This Happens

Content gets indexed into Pinecone (vector database) with metadata. If the indexing script doesn't set the `source` field properly, it defaults to "Unknown".

## Identifying Unknown Sources

Run the diagnostic script:
```bash
cd backend
python scripts/fix_unknown_sources.py --list
```

This will search through your vector store and list all vectors with "Unknown" source, showing:
- Vector ID
- Associated node ID
- Text preview
- Current metadata

## How to Fix It

### Option 1: Re-index with Correct Metadata (Recommended)

This is the cleanest solution. Update your indexing script to include proper metadata, then re-run it.

#### Example: Fixing Bouchaud Book Indexing

1. **Create or update indexing script** (`scripts/index_bouchaud_ch1.py`):

```python
#!/usr/bin/env python3
"""Index Chapter 1 from Bouchaud: Trades, Quotes and Prices"""

import os
import sys
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.database import SessionLocal, Node
from app.services.vector_store import vector_store
import fitz  # PyMuPDF

def index_bouchaud_chapter1():
    """Index Bouchaud Chapter 1 with proper metadata"""

    # Extract content from PDF
    pdf_path = Path(__file__).parent.parent.parent / "content" / "statistics" / "bouchaud_book.pdf"
    doc = fitz.open(pdf_path)

    # Extract Chapter 1 (adjust page numbers as needed)
    chapter1_text = ""
    for page_num in range(16, 40):  # Example page range
        chapter1_text += doc[page_num].get_text()

    doc.close()

    # Split into chunks (simple example - use better chunking in production)
    chunk_size = 2000
    chunks = []
    for i in range(0, len(chapter1_text), chunk_size):
        chunk = chapter1_text[i:i + chunk_size]
        chunks.append({
            'text': chunk,
            'chunk_index': len(chunks),
            'metadata': {
                'category': 'statistics',
                'subcategory': 'heavy_tails',
                'difficulty': 4,
                # ⭐ THIS IS THE KEY - Proper source labeling!
                'source': 'Bouchaud: Trades, Quotes and Prices, Chapter 1',
                'chapter': '1',
                'section': '1.5',  # Optional: specific section
            }
        })

    # Get or create node
    db = SessionLocal()
    node = db.query(Node).filter(Node.slug == 'heavy-tailed-distributions').first()

    if not node:
        node = Node(
            title="Heavy-Tailed Distributions",
            slug="heavy-tailed-distributions",
            category="statistics",
            subcategory="heavy_tails",
            description="Lévy distributions and fat-tailed phenomena",
            difficulty_level=4
        )
        db.add(node)
        db.commit()
        db.refresh(node)

    # Index with proper metadata
    vector_store.upsert_chunks(
        chunks=chunks,
        node_id=node.id,
        node_metadata={
            'title': 'Heavy-Tailed Distributions',
            'category': 'statistics',
            # ⭐ Also set source_book for node-level filtering
            'source_book': 'Bouchaud'
        }
    )

    db.close()
    print(f"✓ Indexed {len(chunks)} chunks with proper source metadata")

if __name__ == "__main__":
    index_bouchaud_chapter1()
```

2. **Run the indexing script:**
```bash
cd backend
python scripts/index_bouchaud_ch1.py
```

This will overwrite the old "Unknown" vectors with properly labeled ones.

### Option 2: Manual Metadata Update (Advanced)

For small updates, you can update individual vectors:

```python
# Example: Update a specific vector's metadata
from app.services.vector_store import vector_store

# Fetch the vector
matches = vector_store.search(query="heavy tails", top_k=10, filter_metadata={'node_id': 42})

# For each match, re-upsert with updated metadata
for match in matches:
    vector_id = match['id']
    embedding = match['values']  # You'd need to fetch this from Pinecone
    metadata = match['metadata']

    # Update metadata
    metadata['source'] = 'Bouchaud: Trades, Quotes and Prices, Chapter 1'
    metadata['chapter'] = '1'

    # Re-upsert
    vector_store.index.upsert(vectors=[{
        'id': vector_id,
        'values': embedding,
        'metadata': metadata
    }])
```

## Proper Metadata Format

### Required Fields

Every indexed chunk MUST include:

```python
metadata = {
    'source': 'Full Book Title, Chapter X',  # MOST IMPORTANT!
    'category': 'statistics | probability | machine_learning | calculus',
    'difficulty': 1-5,
}
```

### Optional But Recommended Fields

```python
metadata = {
    'chapter': '1',  # Chapter number
    'section': '1.5',  # Section number
    'subcategory': 'heavy_tails',  # Specific subtopic
    'page': 23,  # PDF page number
}
```

### Node-Level Metadata

When calling `vector_store.upsert_chunks()`, also provide:

```python
node_metadata = {
    'title': 'Topic Title',
    'category': 'statistics',
    'source_book': 'Short Book Name',  # e.g., 'ESL', 'Bouchaud', 'Deep Learning'
}
```

## Book-Specific Source Labels

Use these standardized source labels for consistency:

```python
# Elements of Statistical Learning
'source': 'Elements of Statistical Learning, Chapter 3'
'source_book': 'ESL'

# Deep Learning: Foundations and Concepts
'source': 'Deep Learning: Foundations and Concepts, Chapter 6'
'source_book': 'Deep Learning'

# Bouchaud: Trades, Quotes and Prices
'source': 'Bouchaud: Trades, Quotes and Prices, Chapter 1'
'source_book': 'Bouchaud'

# Interview Questions / Brain Teasers
'source': 'Quant Interview Questions: Probability'
'source_book': 'Interview Questions'

# Custom Content
'source': 'Your Custom Source Name'
'source_book': 'Custom'
```

## Example: Complete Indexing Script

See `scripts/index_dl_chapter6.py` for a complete, production-ready example with:
- ✅ Proper source metadata
- ✅ Chapter and section tracking
- ✅ Chunking with overlap
- ✅ Error handling
- ✅ Progress logging

Key lines to copy:

```python
# Line 186-191: Per-chunk metadata
'metadata': {
    'category': category,
    'subcategory': subcategory,
    'difficulty': difficulty,
    'source': 'Deep Learning: Foundations and Concepts, Chapter 6',  # ⭐
}

# Line 198-203: Node-level metadata
node_metadata={
    'title': title,
    'category': category,
    'subcategory': subcategory,
    'source_book': 'Deep Learning'  # ⭐
}
```

## Verification

After re-indexing, verify the fix by:

1. **Backend logs:** Run a job description and check the debug output:
```bash
cd backend
uvicorn app.main:app --reload
```

Look for:
```
📚 Topic 'statistical modeling': best match score = 0.549
   └─ Source: Bouchaud: Trades, Quotes and Prices, Chapter 1  ✅
```

2. **Frontend display:** Generate a learning path and verify that topics show the correct book source instead of "Unknown".

3. **Diagnostic script:**
```bash
python scripts/fix_unknown_sources.py --list
```

Should return 0 unknown sources after fixing.

## Common Mistakes to Avoid

❌ **Forgetting to set `source` in metadata dict**
```python
metadata = {
    'category': 'statistics',
    'difficulty': 3
    # Missing 'source'!
}
```

❌ **Using node title instead of book name**
```python
'source': 'Heavy-Tailed Distributions'  # Wrong!
'source': 'Bouchaud: Trades, Quotes and Prices, Chapter 1'  # Correct!
```

❌ **Not including chapter information**
```python
'source': 'Bouchaud'  # Too vague!
'source': 'Bouchaud: Trades, Quotes and Prices, Chapter 1'  # Better!
```

✅ **Correct pattern:**
```python
chunk_data.append({
    'text': chunk_text,
    'chunk_index': i,
    'metadata': {
        'category': 'statistics',
        'subcategory': 'heavy_tails',
        'difficulty': 4,
        'source': 'Bouchaud: Trades, Quotes and Prices, Chapter 1',  # Full source
        'chapter': '1',
        'section': '1.5'
    }
})
```

## Need Help?

If you're still seeing "Unknown" sources after following this guide:

1. Run the diagnostic: `python scripts/fix_unknown_sources.py --list`
2. Check the text preview to identify what content it is
3. Find the corresponding indexing script
4. Add proper `source` metadata
5. Re-run the indexing script
6. Verify with a test query

## Summary

**The Fix in 3 Steps:**

1. Find which content has "Unknown" source:
   ```bash
   python scripts/fix_unknown_sources.py --list
   ```

2. Update the indexing script to include proper metadata:
   ```python
   'source': 'Book Name, Chapter X'
   ```

3. Re-run the indexing script:
   ```bash
   python scripts/index_your_book.py
   ```

Done! Your sources should now display correctly in the learning path view.
