# Professional Setup & Verification System

## Overview

This setup system provides a comprehensive, production-grade verification and setup pipeline for the Quant Learning Platform. It ensures all components are properly configured and data is correctly indexed.

## Quick Start

### Check Current Status

```bash
cd backend
python setup.py --status
```

Output:
```
Status: 🟢 READY

Nodes:          52
Content Chunks: 847
Insights:       26
Users:          3
```

### Run Full Verification

```bash
python setup.py
```

This will:
1. ✓ Check prerequisites (Python, .env, content files)
2. ✓ Verify database (connection, schema, data)
3. ✓ Check content indexing (nodes, chunks)
4. ✓ Verify insights generation
5. → Offer fixes for any issues found

## Architecture

```
backend/
├── setup.py                    # Main orchestrator (run this)
├── setup/
│   ├── config/
│   │   └── content_sources.yaml   # Single source of truth for content
│   └── checks/
│       ├── database.py           # DB verification
│       ├── content.py            # Content indexing checks
│       └── insights.py           # Insights verification
```

## Key Features

### 1. **Idempotent**
Safe to run multiple times. Never destroys data.

### 2. **Self-Diagnosing**
Tells you exactly what's missing or misconfigured.

### 3. **Configuration-Driven**
All content sources defined in `setup/config/content_sources.yaml`:

```yaml
books:
  esl:
    name: "Elements of Statistical Learning"
    path: "content/machine_learning/elements_of_statistical_learning.pdf"
    status: "indexed"
    chapters:
      - number: 3
        title: "Linear Methods for Regression"
        topics: ["Linear Regression", "Ridge Regression"]

  bouchaud:
    name: "Theory of Financial Risk"
    path: "content/statistics/bouchaud_book.pdf"
    status: "partial"
    chapters:
      - number: 1
        title: "Probability Theory"
        enhancement_target: "content/statistics/inference_enhanced.md"
        status: "enhanced"
```

### 4. **Extensible**
Adding a new book? Just update `content_sources.yaml`:

```yaml
books:
  new_book:
    name: "Your New Book"
    path: "content/category/book.pdf"
    requires_indexing: true
    requires_insights: true
    chapters: [...]
```

### 5. **Clear Status Reporting**

Example output:
```
═══════════════════════════════════════════════════════════════════════════════
1. Checking Prerequisites
═══════════════════════════════════════════════════════════════════════════════

  ✓ Python 3.11 ✓
  ✓ .env configuration file exists
  ✓ DATABASE_URL configured
  ✓ OPENAI_API_KEY configured
  ✓ PINECONE_API_KEY configured
  ✓ ESL book present (13.0 MB)
  ✓ DL book present (48.2 MB)
  ✓ Bouchaud book present (25.0 MB)

═══════════════════════════════════════════════════════════════════════════════
2. Checking Database
═══════════════════════════════════════════════════════════════════════════════

  ✓ Database connection successful
  ✓ All 7 required tables exist
  ✓ All table schemas valid

  Current Data:
    • Nodes: 52
    • Content Chunks: 847
    • Insights: 26
    • Users: 3

[... continues ...]
```

## Usage Patterns

### Fresh Setup (New Developer)

```bash
# 1. Clone repo
git clone <repo>
cd Quants_Learn/backend

# 2. Create .env
cp .env.example .env
# Edit .env with your API keys

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run setup
python setup.py

# 5. Follow prompts to initialize database and index content
```

### Daily Development

```bash
# Quick status check
python setup.py --status

# Full verification before working
python setup.py --check-only
```

### After Adding New Content

```bash
# 1. Update content_sources.yaml
vim setup/config/content_sources.yaml

# 2. Run verification
python setup.py

# 3. System will detect missing content and suggest:
#    → python scripts/index_content.py --category statistics
```

### Before Deployment

```bash
# Run full check (non-interactive)
python setup.py --check-only

# Exit code 0 = ready, 1 = issues found
```

## Content Management

### Adding a New Book

1. **Add PDF to content directory**:
   ```bash
   cp new_book.pdf content/category/
   ```

2. **Update `content_sources.yaml`**:
   ```yaml
   books:
     new_book_id:
       name: "New Book Name"
       path: "content/category/new_book.pdf"
       category: "statistics"
       requires_indexing: true
       requires_insights: false
       chapters:
         - number: 1
           title: "Chapter 1"
           topics: ["Topic A", "Topic B"]
       status: "planned"
   ```

3. **Run verification**:
   ```bash
   python setup.py
   ```

4. **System will show**:
   ```
   Book Content Status:
     ✓ New Book Name: planned (0/2 topics indexed)

   → Suggestion: python scripts/index_new_book_ch1.py
   ```

### Updating Content (e.g., Adding Bouchaud Ch 2)

1. **Update status in `content_sources.yaml`**:
   ```yaml
   bouchaud:
     chapters:
       - number: 2
         title: "Extreme Value Theory"
         topics: ["EVT", "Large Deviations"]
         status: "planned"  # Change from "planned" to "enhanced" when done
   ```

2. **Create enhancement script** (if needed):
   ```bash
   python scripts/extract_bouchaud_ch2_evt.py
   ```

3. **Update content file**:
   ```bash
   # Add Bouchaud Ch2 content to relevant file
   vim content/statistics/extreme_events.md
   ```

4. **Reindex**:
   ```bash
   python scripts/reindex_statistics.py
   ```

5. **Verify**:
   ```bash
   python setup.py
   ```

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: Verify Setup

on: [push, pull_request]

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt

      - name: Run setup verification
        run: |
          cd backend
          python setup.py --check-only
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

## Troubleshooting

### "Database connection failed"
```bash
# Check DATABASE_URL in .env
cat .env | grep DATABASE_URL

# Test connection manually
psql $DATABASE_URL
```

### "No content chunks in database"
```bash
# Index all content
python scripts/index_content.py --init-db

# Verify
python setup.py --status
```

### "No insights in database"
```bash
# Generate insights for ESL topics
python scripts/generate_all_insights.py

# Verify
python setup.py
```

## Philosophy

This setup system follows these principles:

1. **Configuration as Documentation** - `content_sources.yaml` is the single source of truth
2. **Fail Fast, Fail Clear** - Issues are detected early with clear error messages
3. **Progressive Enhancement** - System works with partial data, shows what's missing
4. **Developer-Friendly** - Clear commands, helpful suggestions, colored output
5. **Production-Ready** - Same checks work locally and in CI/CD

## Future Enhancements

Potential additions:
- Automatic content indexing when new books added
- Webhook to trigger reindexing on content changes
- Health check HTTP endpoint for monitoring
- Metrics export (Prometheus format)
- Setup wizard for first-time users
- Content versioning and migration system
