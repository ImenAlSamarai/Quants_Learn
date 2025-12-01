# Quick Start: Web Content Crawling & Integration

## Prerequisites

1. **Set up .env file:**
   ```bash
   cd backend
   cp .env.example .env
   nano .env
   ```
   Add your API keys:
   ```
   PINECONE_API_KEY=your_key_here
   OPENAI_API_KEY=your_key_here
   ANTHROPIC_API_KEY=your_key_here  # Optional
   ```

2. **Verify setup:**
   ```bash
   python test_web_rag.py
   ```

## Common Workflows

### Workflow 1: Index Single Article

**Use when:** You find a specific high-quality article

```bash
python scripts/index_web_resource.py \
  --url https://example.com/article \
  --topic "Maximum Likelihood Estimation" \
  --source-name "Towards Data Science"
```

**Result:** Single page indexed, immediately usable in learning paths

---

### Workflow 2: Batch Index Multiple URLs

**Use when:** You have a list of curated URLs

```bash
# Create urls.txt
cat > urls.txt << EOF
https://example.com/article1
https://example.com/article2
https://example.com/article3
EOF

# Index all
python scripts/batch_index_urls.py \
  --url-file urls.txt \
  --topic "Statistical Modeling"
```

**Result:** All URLs indexed with same topic tag

---

### Workflow 3: Multi-Topic Single Page

**Use when:** One page covers multiple topics

```bash
python scripts/index_url_multitopic.py \
  --url https://example.com/comprehensive-guide \
  --topics "Bayesian Inference" "MCMC" "Variational Inference"
```

**Result:** Each chunk tagged with ALL topics for better matching

---

### Workflow 4: Auto-Crawl Documentation Site

**Use when:** You want to index entire documentation sites

```bash
python scripts/crawl_and_index.py \
  --url https://docs.example.com/ \
  --depth 3 \
  --max-pages 100
```

**What it does:**
- ✅ Auto-discovers subpages (BFS traversal)
- ✅ Auto-extracts topic from each page title
- ✅ Respects robots.txt
- ✅ Rate-limited (2s delay between requests)
- ✅ Deduplicates URLs

**Advanced options:**
```bash
# Only crawl specific patterns
python scripts/crawl_and_index.py \
  --url https://docs.example.com/ \
  --depth 2 \
  --max-pages 50 \
  --pattern "*/tutorials/*"

# Stay on same domain (default)
python scripts/crawl_and_index.py \
  --url https://docs.example.com/ \
  --same-domain
```

---

## Real-World Examples

### Example 1: Index PyMC Documentation

```bash
python scripts/crawl_and_index.py \
  --url https://www.pymc.io/projects/docs/en/stable/ \
  --depth 2 \
  --max-pages 50 \
  --topic "Probabilistic Programming"
```

**Coverage improvement:** 0% → 85% for "probabilistic programming"

---

### Example 2: Index Scikit-Learn Tutorials

```bash
python scripts/crawl_and_index.py \
  --url https://scikit-learn.org/stable/tutorial/ \
  --depth 2 \
  --max-pages 30
```

**Topics auto-detected:** Ridge Regression, Lasso, Cross-Validation, etc.

---

### Example 3: Index Options Pricing Blog

```bash
python scripts/crawl_and_index.py \
  --url https://www.innovation-options.com/learn.html \
  --depth 2 \
  --max-pages 20
```

**Result:** 20 pages indexed covering real options, innovation metrics, NPV analysis

---

## Monitoring & Verification

### Check what was indexed

```python
from app.services.vector_store import vector_store

# Get namespace stats
stats = vector_store.get_index_stats()
print(f"Web resource vectors: {stats['namespaces']['web_resource']['vector_count']}")

# Test search
results = vector_store.search(
    query="option pricing",
    namespace="web_resource",
    top_k=5
)

for r in results:
    print(f"{r['score']:.3f} - {r['metadata']['url']}")
```

### Run learning path to see coverage

```bash
python main.py
```

Look for 🌐 WEB sources in output!

---

## Crawler Configuration

**Edit:** `backend/scripts/crawl_and_index.py`

**Key parameters:**

```python
class WebCrawler:
    def __init__(
        self,
        start_url: str,
        max_depth: int = 2,          # How deep to crawl
        max_pages: int = 50,          # Max pages to index
        same_domain: bool = True,     # Stay on same domain
        url_pattern: str = None,      # Filter URLs (e.g., "*/docs/*")
        delay: float = 2.0,           # Delay between requests (seconds)
        chunk_size: int = 2000,       # Characters per chunk
        chunk_overlap: int = 200      # Overlap between chunks
    ):
```

**Topic extraction patterns:**

```python
# Customize in extract_topic_from_title()
prefixes_to_remove = [
    r'^Documentation[\s\-:]+',
    r'^Docs[\s\-:]+',
    r'^Tutorial[\s\-:]+',
    r'^Guide[\s\-:]+',
    r'^\d+\.\d+\.\d+[\s\-:]+',  # Version numbers
]
```

---

## Best Practices

### ✅ DO:

1. **Start small, scale up**
   - Test with `--max-pages 5` first
   - Verify quality before crawling full site

2. **Check robots.txt**
   - Crawler respects it, but verify manually
   - Some sites block automated crawling

3. **Use appropriate delays**
   - Default 2s is safe
   - Increase for slower sites
   - Respect rate limits

4. **Monitor token usage**
   - Embeddings cost $0.00002/1K tokens
   - 1000 chunks ≈ $0.04

5. **Verify content quality**
   - Run test searches after indexing
   - Check that chunks contain useful content

### ❌ DON'T:

1. **Don't crawl entire internet**
   - Target specific, high-quality sources
   - Use curated documentation sites

2. **Don't ignore rate limits**
   - Respect `delay` parameter
   - Don't set `--delay 0`

3. **Don't index low-quality content**
   - Check page content before crawling
   - Avoid marketing pages, ads, etc.

4. **Don't mix unrelated topics**
   - Keep each crawl focused on one domain
   - Use separate crawls for different topics

---

## Troubleshooting

### "Connection refused" or "Timeout"

**Cause:** Site blocking automated requests

**Fix:**
- Check robots.txt
- Increase `--delay`
- Use manual indexing instead

### "No text content found"

**Cause:** JavaScript-heavy site

**Fix:**
- Some sites require JS rendering
- Use manual URL indexing for specific pages
- Consider using Selenium for JS sites

### "Topic extraction returning generic names"

**Cause:** Page titles not descriptive

**Fix:**
- Edit `extract_topic_from_title()` patterns
- Or manually specify `--topic` parameter

### "Embeddings taking too long"

**Cause:** Many chunks to process

**Fix:**
- Reduce `--max-pages`
- Increase `chunk_size` (fewer chunks)
- Process in smaller batches

---

## Cost Estimation

**Assumptions:**
- Average page: 5000 characters
- Chunk size: 2000 characters
- Average chunks per page: 3
- Embedding cost: $0.00002/1K tokens
- 1 char ≈ 0.25 tokens (conservative)

**Example: 100 pages**
```
100 pages × 3 chunks × 2000 chars × 0.25 tokens/char = 150K tokens
Cost: 150K × $0.00002 = $0.003 (less than 1 cent!)
```

**Embedding costs are VERY cheap!** 🎉

---

## Next Steps

1. **Set up .env file** ← Start here!
2. **Run test:** `python test_web_rag.py`
3. **Index first site:** Use one of the examples above
4. **Generate learning path:** `python main.py`
5. **Verify web content appears** in coverage analysis
6. **Scale up:** Crawl more sites as needed

---

**Need help?** Check `WEB_CONTENT_INTEGRATION.md` for detailed architecture docs.
