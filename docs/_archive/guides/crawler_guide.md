# Web Crawler Guide

Automatically discover and index multiple pages from a website.

---

## 🚀 Quick Start

### **Example 1: Crawl Documentation Section**

```bash
cd /home/user/Quants_Learn/backend

# Crawl Scikit-Learn linear models documentation (2 levels deep)
python scripts/crawl_and_index.py \
    --url "https://scikit-learn.org/stable/modules/linear_model.html" \
    --depth 2 \
    --pattern "*/modules/linear_model*" \
    --topic "Linear Models" \
    --max-pages 20
```

**What happens:**
1. Starts at the linear models page
2. Finds all links on that page
3. Visits linked pages (up to 2 levels deep)
4. Only visits pages matching `*/modules/linear_model*`
5. Indexes up to 20 pages
6. Respects robots.txt
7. Waits 2 seconds between requests

### **Example 2: Crawl Blog Category**

```bash
# Index first 10 articles from Towards Data Science statistics category
python scripts/crawl_and_index.py \
    --url "https://towardsdatascience.com/tagged/statistics" \
    --depth 1 \
    --max-pages 10 \
    --topic "Statistics" \
    --source "Towards Data Science"
```

### **Example 3: Crawl Tutorial Series**

```bash
# Index Python tutorial (all pages in the tutorial section)
python scripts/crawl_and_index.py \
    --url "https://docs.python.org/3/tutorial/" \
    --depth 2 \
    --topic "Python Tutorial" \
    --source "Python Docs" \
    --max-pages 30
```

---

## 📊 Parameters Explained

| Parameter | Description | Default | Example |
|-----------|-------------|---------|---------|
| `--url` | Starting URL (required) | - | `https://example.com` |
| `--depth` | How many levels deep to crawl | 2 | `--depth 3` |
| `--max-pages` | Maximum pages to index | 100 | `--max-pages 20` |
| `--pattern` | URL pattern to match | None (all) | `--pattern "*/docs/*"` |
| `--topic` | Topic name for all pages | Auto-detect | `--topic "Machine Learning"` |
| `--source` | Source name | Auto-detect | `--source "Scikit-Learn"` |
| `--delay` | Seconds between requests | 2 | `--delay 5` |
| `--allow-external` | Crawl external domains | False | `--allow-external` |

---

## 🎯 Use Cases

### **Use Case 1: Complete Documentation Site**

```bash
# Index all PyTorch nn.Module documentation
python scripts/crawl_and_index.py \
    --url "https://pytorch.org/docs/stable/nn.html" \
    --depth 2 \
    --pattern "*/docs/stable/nn*" \
    --topic "PyTorch Neural Networks" \
    --max-pages 50 \
    --delay 3
```

### **Use Case 2: Research Paper Series**

```bash
# Index ArXiv papers from a specific series
python scripts/crawl_and_index.py \
    --url "https://arxiv.org/list/stat.ML/recent" \
    --depth 1 \
    --max-pages 15 \
    --topic "Statistical Machine Learning" \
    --source "ArXiv"
```

### **Use Case 3: Educational Resource**

```bash
# Index Seeing Theory (interactive statistics)
python scripts/crawl_and_index.py \
    --url "https://seeing-theory.brown.edu/" \
    --depth 2 \
    --topic "Statistics Visualization" \
    --source "Seeing Theory" \
    --max-pages 25
```

---

## ✅ Safety Features

### **1. Respects robots.txt**
- Automatically checks `https://example.com/robots.txt`
- Skips disallowed URLs
- User-Agent: "Educational Crawler"

### **2. Rate Limiting**
- Default: 2 seconds between requests
- Adjustable with `--delay`
- Be respectful to servers!

### **3. Same-Domain Only (Default)**
- Won't crawl external sites by default
- Use `--allow-external` to override (use carefully!)

### **4. URL Filtering**
Automatically skips:
- Login/signup pages
- Shopping cart/checkout
- API endpoints
- Binary files (PDF, ZIP)
- Search queries

### **5. Deduplication**
- Tracks visited URLs
- Won't index same page twice
- Removes URL fragments

---

## 📋 Pattern Matching

Use `--pattern` to stay within specific sections:

### **Documentation Sections**
```bash
# Only Scikit-Learn supervised learning docs
--pattern "*/modules/supervised*"

# Only PyTorch tutorials
--pattern "*/tutorials/*"

# Only specific version docs
--pattern "*/docs/stable/*"
```

### **Blog Categories**
```bash
# Only articles with "machine-learning" tag
--pattern "*/tagged/machine-learning/*"

# Only posts in 2024
--pattern "*/2024/*"
```

### **Wildcards**
- `*` matches any characters
- `?` matches single character
- `[abc]` matches a, b, or c

---

## ⚠️ Important Warnings

### **1. Start Small**
```bash
# TEST with small limits first
python scripts/crawl_and_index.py \
    --url "https://example.com" \
    --depth 1 \
    --max-pages 5  # Small limit for testing
```

### **2. Respect Server Resources**
```bash
# Increase delay for busy sites
--delay 5  # 5 seconds instead of 2

# Limit pages
--max-pages 20  # Don't crawl entire site
```

### **3. Check robots.txt Manually**
```bash
# Before crawling, check what's allowed
curl https://example.com/robots.txt
```

### **4. Don't Crawl Paywalled Content**
- Respects robots.txt but won't bypass paywalls
- Don't crawl sites requiring authentication
- Use official APIs when available

---

## 🔍 Monitoring Progress

The crawler prints detailed progress:

```
================================================================================
WEB CRAWLER STARTING
================================================================================
Start URL: https://scikit-learn.org/stable/modules/linear_model.html
Max Depth: 2
Max Pages: 20
Same Domain: True
Pattern: */modules/linear_model*
================================================================================

✅ Loaded robots.txt from https://scikit-learn.org/robots.txt

[1/20] Depth 0: https://scikit-learn.org/stable/modules/linear_model.html
  🔗 Found 45 links
  📝 12 chunks
  ✅ Indexed: Linear Models

[2/20] Depth 1: https://scikit-learn.org/stable/modules/linear_model.html#ordinary-least-squares
  🔗 Found 38 links
  📝 8 chunks
  ✅ Indexed: Ordinary Least Squares

...

================================================================================
CRAWL COMPLETE
================================================================================
Pages indexed: 18
Pages visited: 18
Pages remaining: 27
================================================================================
```

---

## 🚦 Advanced Usage

### **Crawl Multiple Starting Points**

```bash
# Create a list of starting URLs
cat > crawl_starts.txt << 'EOF'
https://scikit-learn.org/stable/modules/linear_model.html
https://scikit-learn.org/stable/modules/tree.html
https://scikit-learn.org/stable/modules/ensemble.html
EOF

# Crawl each
while read url; do
    python scripts/crawl_and_index.py \
        --url "$url" \
        --depth 1 \
        --max-pages 10 \
        --delay 3
done < crawl_starts.txt
```

### **Verify Indexing**

```bash
# After crawling, verify pages are searchable
python -c "
from app.services.vector_store import vector_store

# Search for content from crawled pages
results = vector_store.search('linear regression scikit-learn', top_k=5)

print(f'Found {len(results)} results:\n')
for r in results:
    print(f'{r['score']:.3f} - {r['metadata']['source']}')
    print(f'  URL: {r['metadata'].get('url', 'N/A')}')
    print(f'  Depth: {r['metadata'].get('crawl_depth', 'N/A')}')
    print()
"
```

---

## 🆚 Comparison: Crawler vs Manual Indexing

| Feature | Manual (`batch_index_urls.py`) | Crawler (`crawl_and_index.py`) |
|---------|-------------------------------|-------------------------------|
| **URLs** | List specific URLs | Auto-discovers URLs |
| **Control** | Precise control | Automated discovery |
| **Speed** | Fast (only listed URLs) | Slower (explores links) |
| **Coverage** | Only what you list | Comprehensive within limits |
| **Best For** | Known URLs, curated lists | Documentation sites, blogs |

---

## 💡 Best Practices

### **1. Documentation Sites**
✅ **Do**: Crawl with pattern matching
```bash
python scripts/crawl_and_index.py \
    --url "https://docs.example.com/" \
    --pattern "*/docs/api/*" \
    --max-pages 50
```

❌ **Don't**: Crawl entire site without limits
```bash
# BAD: No limits, might index thousands of pages
python scripts/crawl_and_index.py --url "https://docs.example.com/" --depth 10
```

### **2. Blogs/Articles**
✅ **Do**: Use max-pages limit
```bash
python scripts/crawl_and_index.py \
    --url "https://blog.example.com/category/ml/" \
    --max-pages 20  # Just top 20 articles
```

### **3. Rate Limiting**
✅ **Do**: Be respectful
```bash
# For busy sites, increase delay
--delay 5  # 5 seconds between requests
```

---

## 🔧 Troubleshooting

### **"Blocked by robots.txt"**
- Some sites disallow crawling
- Check `https://example.com/robots.txt`
- Use manual indexing instead

### **"Too many pages discovered"**
- Use `--pattern` to filter URLs
- Lower `--depth`
- Set stricter `--max-pages`

### **"Server errors (429, 503)"**
- Increase `--delay`
- Lower `--max-pages`
- Crawl in smaller batches

---

## 📚 Complete Example

```bash
# Goal: Index all Scikit-Learn regression documentation

# 1. Test with small limits first
python scripts/crawl_and_index.py \
    --url "https://scikit-learn.org/stable/modules/linear_model.html" \
    --depth 1 \
    --max-pages 3 \
    --topic "Regression Methods"

# 2. If successful, increase limits
python scripts/crawl_and_index.py \
    --url "https://scikit-learn.org/stable/modules/linear_model.html" \
    --depth 2 \
    --max-pages 25 \
    --pattern "*/modules/linear_model*" \
    --topic "Linear Models" \
    --source "Scikit-Learn Docs" \
    --delay 3

# 3. Verify indexing
python -c "
from app.services.learning_path_service import learning_path_service
coverage = learning_path_service.check_topic_coverage('Linear Regression')
print(f'Covered: {coverage['covered']}')
print(f'Confidence: {coverage['confidence']:.3f}')
print(f'Sources: {coverage.get('source', 'N/A')}')
"

# 4. Use in learning path
# Paste job description → Topics extracted → Crawled content used!
```

---

**Now you can explore and index entire documentation sites automatically!** 🚀
