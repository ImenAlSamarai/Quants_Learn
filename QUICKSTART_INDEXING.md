# 🚀 Quick Start: Index Your New Book

## TL;DR - Three Commands

```bash
cd /Users/imenalsamarai/Documents/projects_MCP/Quants_Learn/backend
source venv/bin/activate

# 1. See what's ready to index
python scripts/universal_book_indexer.py --scan

# 2. Index new books (safe - won't break existing content)
python scripts/universal_book_indexer.py --index-new
```

## 📋 For "Advances in Financial Machine Learning"

### Step 1: Put PDF in content folder

Already done if you added it! It can be in any subfolder:
- ✅ `content/machine_learning/advances_in_financial_ml.pdf`
- ✅ `content/finance/advances_in_financial_ml.pdf` (if you create this folder)
- ✅ `content/books/advances_in_financial_ml.pdf`

**Location doesn't matter** - the database handles categorization!

### Step 2: Register the book

The book is **already registered** in `universal_book_indexer.py`!

Look for this entry in `BOOK_REGISTRY`:

```python
"advances_in_financial_ml.pdf": {
    "title": "Advances in Financial Machine Learning",
    "short_name": "AFML",
    "primary_category": "finance",
    "secondary_categories": ["machine_learning", "statistics"],
    "chapters": [
        # Add chapter definitions here as you want to index them
    ]
}
```

**To index chapters**, add them like this:

```python
"chapters": [
    {"num": 1, "title": "Financial Data Structures", "subcategory": "data_structures", "difficulty": 3},
    {"num": 2, "title": "Financial Features", "subcategory": "feature_engineering", "difficulty": 4},
    # ... add more chapters as needed
]
```

### Step 3: Run the indexer

```bash
cd backend
source venv/bin/activate

# See status
python scripts/universal_book_indexer.py --scan

# Index the new book
python scripts/universal_book_indexer.py --index-new
```

### Step 4: Verify

```bash
# Check what got indexed
python scripts/check_indexed_content.py

# Start the app
python -m app.main
```

## 📝 Important Notes

### ✅ Safe to Run Multiple Times

The indexer:
- ✅ Checks if content already exists before indexing
- ✅ Skips already-indexed chapters
- ✅ Shows what it will do before doing it (`--scan`)
- ✅ Won't break existing content

### 🏷️ Multi-Category System

Your book gets tagged with:
- **Primary category**: `finance` (main classification)
- **Secondary tags**: `machine_learning`, `statistics` (cross-domain)

This means:
- Shows up primarily in "Finance" category
- Also discoverable when users explore ML or Stats topics
- Future: Can filter by multiple categories

### 📂 Folder Structure Decision

**Current recommendation**: Keep subfolders as-is

```
content/
├── machine_learning/
│   ├── elements_of_statistical_learning.pdf
│   ├── deep_learning_foundations_and_concepts.pdf
│   └── advances_in_financial_ml.pdf          # ← Put it here
├── statistics/
│   └── bouchaud_book.pdf
└── probability/
    └── [future books]
```

**Why?**
- Database stores the real categorization (not folder structure)
- No code changes needed
- Can reorganize later without reindexing

**Alternative**: Create `content/finance/` folder if you prefer semantic organization.

## 🔧 Advanced Usage

### Index a Specific Book Only

```bash
python scripts/universal_book_indexer.py --book "advances_in_financial_ml.pdf"
```

### Initialize Database First (if needed)

```bash
python scripts/universal_book_indexer.py --init-db --index-new
```

### Check What Will Be Indexed (Safe Preview)

```bash
python scripts/universal_book_indexer.py --scan
```

Output:
```
📚 UNIVERSAL BOOK INDEXER - SCAN REPORT
================================================================
📊 Summary:
  Total PDFs found: 4
  Ready to index: 1

🆕 Ready to Index:
  → Advances in Financial Machine Learning (AFML) - 2 chapters defined
```

## 🐛 Troubleshooting

### "No chapters defined in BOOK_REGISTRY"

**Solution**: Add chapter definitions to the book entry:

```python
"advances_in_financial_ml.pdf": {
    # ... existing config ...
    "chapters": [
        {"num": 1, "title": "Chapter Title", "subcategory": "topic", "difficulty": 3},
    ]
}
```

### "PDF not found"

**Solution**: Check the filename matches exactly:

```bash
ls -la content/machine_learning/*.pdf
# Should show: advances_in_financial_ml.pdf
```

### "ModuleNotFoundError: No module named 'X'"

**Solution**: Install dependencies:

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### Want to Re-index a Book?

If you need to re-index (e.g., updated PDF):

```bash
# Clear the existing nodes first
python manage.py clear-cache --all

# Then re-index
python scripts/universal_book_indexer.py --book "your_book.pdf"
```

## 📚 Full Documentation

- **Strategy & Architecture**: See `INDEXING_STRATEGY.md`
- **Complete README**: See `README.md`
- **Management Commands**: See `README.md` section "Management CLI"

---

**Need Help?** Check `INDEXING_STRATEGY.md` for detailed explanation of the multi-category system!
