# Content Directory Management

## Books and Documents Removed from Remote Repository

For security and copyright compliance, all books and documents have been removed from the remote GitHub repository.

### Files Removed

The following files were removed from git tracking and the remote repository:

1. `content/machine_learning/deep_learning_foundations_and_concepts.pdf` (48 MB)
2. `content/machine_learning/elements_of_statistical_learning.pdf` (13 MB)
3. `content/statistics/bouchaud_book.pdf` (25 MB)

**Total size removed:** ~86 MB

### Files Still Available Locally

✅ All books remain in your local `content/` directory
✅ The indexing system can still use them for RAG
✅ They just won't be pushed to GitHub

### Updated .gitignore

The `.gitignore` file now blocks all document formats from being committed:

```gitignore
# All books and documents in content directory
content/**/*.pdf
content/**/*.epub
content/**/*.mobi
content/**/*.djvu
content/**/*.docx
content/**/*.doc
content/**/*.txt
content/**/*.md

# Keep only index/metadata files
!content/**/index.json
!content/**/metadata.json
!content/**/README.md
```

### What This Means

**✅ Safe to commit:**
- `content/**/index.json` - Book metadata
- `content/**/metadata.json` - Indexing information
- `content/**/README.md` - Documentation
- Python scripts in `backend/scripts/`
- Application code

**❌ Blocked from commit:**
- PDFs, EPUBs, MOBIs, DJVU files
- Word documents (docx, doc)
- Text files in content/ directory
- Any book or document content

### For Other Developers

**To set up the content directory:**

1. Create the content structure:
   ```bash
   mkdir -p content/machine_learning
   mkdir -p content/statistics
   mkdir -p content/confidential
   ```

2. Add your own books (not committed to git):
   ```bash
   # Copy your books locally
   cp ~/Downloads/your_book.pdf content/machine_learning/
   ```

3. Index the books:
   ```bash
   cd backend
   python scripts/index_document.py \
     --file ../content/machine_learning/your_book.pdf \
     --category "Machine Learning" \
     --book-title "Your Book Title"
   ```

4. Books stay local, only the Pinecone vectors are shared (via your Pinecone account).

### Why This Matters

1. **Copyright Protection:** Distributing copyrighted books via GitHub violates copyright law
2. **Repository Size:** Books are large files (86 MB just for 3 books)
3. **Security:** Prevents accidental exposure of proprietary materials
4. **Best Practice:** Content is indexed to Pinecone, not stored in git

### Verification

Check what's tracked by git:
```bash
git ls-files content/
```

Should only show metadata files, not PDFs or documents.

Check what's local:
```bash
ls -lh content/**/*.pdf
```

Should show your books are still there locally.

---

**Status:** ✅ Complete - No books in remote repository, all content available locally for indexing
