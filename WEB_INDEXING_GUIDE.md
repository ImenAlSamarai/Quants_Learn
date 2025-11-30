# Universal Web Indexing Guide

Complete guide for indexing web content (articles, tutorials, documentation) into your RAG system.

---

## 🚀 Quick Start

### **Method 1: Single URL (Fastest)**

```bash
cd /home/user/Quants_Learn/backend

# Index a single article
python scripts/batch_index_urls.py \
    --url "https://towardsdatascience.com/understanding-maximum-likelihood" \
    --topic "Maximum Likelihood Estimation"

# With custom source name
python scripts/batch_index_urls.py \
    --url "https://stats.stackexchange.com/questions/12345" \
    --topic "Bayesian Inference" \
    --source "Cross Validated"
```

### **Method 2: Batch from File (Recommended for Multiple URLs)**

```bash
# 1. Edit the URLs file
nano scripts/index_urls.txt

# 2. Add your URLs (format: URL | Topic | Source)
https://towardsdatascience.com/article1 | Maximum Likelihood | Towards Data Science
https://scikit-learn.org/stable/linear_model.html | Linear Regression | Scikit-Learn
https://stats.stackexchange.com/questions/789 | Bayesian Methods | Cross Validated

# 3. Run batch indexer
python scripts/batch_index_urls.py --file scripts/index_urls.txt
```

### **Method 3: Multiple URLs Inline**

```bash
python scripts/batch_index_urls.py --urls \
    "https://url1.com,Topic 1,Source 1" \
    "https://url2.com,Topic 2,Source 2" \
    "https://url3.com,Topic 3"
```

---

## 📋 Complete Workflow

### **Step 1: Prepare Your URLs**

Create `scripts/index_urls.txt`:
```
# Web Resources for Statistical Modeling
https://towardsdatascience.com/maximum-likelihood-estimation-984af2dcfcac | Maximum Likelihood Estimation | Towards Data Science
https://towardsdatascience.com/bayesian-inference-intuition-and-example | Bayesian Inference | Towards Data Science
https://scikit-learn.org/stable/modules/linear_model.html | Linear Regression | Scikit-Learn Docs

# Stack Exchange Q&A
https://stats.stackexchange.com/questions/2641/what-is-the-difference-between-likelihood-and-probability | Likelihood vs Probability | Cross Validated
https://quant.stackexchange.com/questions/1234/black-scholes-derivation | Black-Scholes Model | Quant Stack Exchange

# Academic Resources
https://distill.pub/2019/visual-exploration-gaussian-processes/ | Gaussian Processes | Distill.pub
https://colah.github.io/posts/2015-08-Backprop/ | Backpropagation | Colah's Blog
```

### **Step 2: Index the URLs**

```bash
cd /home/user/Quants_Learn/backend
python scripts/batch_index_urls.py --file scripts/index_urls.txt
```

**Output:**
```
================================================================================
BATCH WEB INDEXING - 7 URLs
================================================================================

[1/7] Processing: Maximum Likelihood Estimation
  URL: https://towardsdatascience.com/maximum-likelihood-estimation-984af2dcfcac
📡 Fetching https://towardsdatascience.com/...
✅ Fetched: Maximum Likelihood Estimation Explained (12453 chars)
📝 Split into 15 chunks
🚀 Indexing to Pinecone...
✅ Indexed 15 chunks from https://towardsdatascience.com/...
   Topic: Maximum Likelihood Estimation
   Source: Towards Data Science
   Category: web_resource/online_article

  ⏱️  Waiting 2 seconds before next request...

[2/7] Processing: Bayesian Inference
...

================================================================================
BATCH INDEXING COMPLETE
================================================================================
✅ Success: 7/7
❌ Failed: 0/7
```

### **Step 3: Verify Indexing**

```bash
# Check if content is searchable
python -c "
from app.services.vector_store import vector_store

results = vector_store.search('maximum likelihood estimation', top_k=5)

print(f'Found {len(results)} results:\n')
for r in results:
    print(f'{r['score']:.3f} - {r['metadata'].get('source', 'Unknown')}')
    print(f'  Topic: {r['metadata'].get('topic', 'N/A')}')
    print(f'  URL: {r['metadata'].get('url', 'N/A')}')
    print()
"
```

### **Step 4: Use in Learning Path**

```bash
# Start the app
python app/main.py

# Paste job description mentioning "maximum likelihood estimation"
# → Should detect topic
# → Should find coverage from indexed web resources
# → Should generate content using web article chunks
```

---

## 🌐 Supported Websites

### ✅ **Works Great**

| Site | Example | Notes |
|------|---------|-------|
| Medium (Towards Data Science) | `towardsdatascience.com/article` | Clean extraction |
| Stack Exchange | `stats.stackexchange.com/questions/123` | Q&A format works well |
| Scikit-Learn Docs | `scikit-learn.org/stable/modules/...` | Technical docs |
| Distill.pub | `distill.pub/2019/...` | Academic articles |
| GitHub blogs | `colah.github.io/posts/...` | Personal blogs |
| ArXiv (HTML) | `arxiv.org/html/2301.12345` | Research papers |
| PyTorch Docs | `pytorch.org/docs/stable/...` | Framework docs |
| Real Python | `realpython.com/tutorials/...` | Python tutorials |

### ⚠️ **May Need Special Handling**

| Site | Issue | Solution |
|------|-------|----------|
| Paywalled sites (Bloomberg, WSJ) | Login required | Use archive.org or public summaries |
| Heavy JavaScript sites | Content loaded dynamically | Add Selenium support (see below) |
| PDFs embedded in pages | Not extracted | Use `index_document.py` instead |
| YouTube (video content) | No transcripts extracted | Get transcript first, then index |

### ❌ **Not Supported**

- Sites requiring authentication (LinkedIn, private forums)
- Video content without transcripts
- Image-heavy tutorials without text
- Flash/Java applets (very old sites)

---

## 🔧 Advanced Usage

### **Custom Categories**

Organize by domain:
```bash
# Trading resources
python scripts/batch_index_urls.py \
    --file trading_urls.txt \
    --category trading

# Statistics resources
python scripts/batch_index_urls.py \
    --file stats_urls.txt \
    --category statistics
```

### **Handle JavaScript-Heavy Sites**

For React/Angular sites that don't render server-side:

```bash
# Install Selenium
pip install selenium webdriver-manager

# Modify index_web_resource.py to use Selenium
# (See code example below)
```

<details>
<summary>Click to see Selenium code example</summary>

```python
# Add to index_web_resource.py

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def fetch_webpage_selenium(self, url: str) -> dict:
    """Fetch webpage using Selenium for JavaScript-heavy sites"""

    print(f"📡 Fetching {url} with Selenium...")

    # Setup headless Chrome
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )

    try:
        driver.get(url)

        # Wait for page to load (adjust selector as needed)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        # Get page source
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        # Rest is same as regular fetch_webpage()
        title = soup.find('title')
        title_text = title.get_text().strip() if title else urlparse(url).path

        # ... (same extraction logic)

        return {'title': title_text, 'text': text, 'url': url, 'domain': domain}

    finally:
        driver.quit()
```
</details>

### **Rate Limiting**

The batch indexer waits 2 seconds between requests by default. Adjust in code:

```python
# In batch_index_urls.py, line ~85
time.sleep(5)  # Wait 5 seconds instead of 2
```

### **Verify Before Large Batch**

Test with 1-2 URLs first:
```bash
# Test single URL
python scripts/batch_index_urls.py \
    --url "https://test-url.com" \
    --topic "Test Topic"

# Verify it worked
python -c "
from app.services.vector_store import vector_store
results = vector_store.search('Test Topic', top_k=1)
print(f'Success! Found: {results[0]['metadata']['source']}')
"

# If successful, run full batch
python scripts/batch_index_urls.py --file scripts/index_urls.txt
```

---

## 📊 Usage Patterns

### **Pattern 1: Job-Specific Resources**

```bash
# 1. Get job description mentioning specific tools/frameworks
# 2. Find relevant tutorials/docs for those tools
# 3. Create urls file:

# For "Python + PyTorch + Transformers" job
https://pytorch.org/tutorials/beginner/basics/intro.html | PyTorch Basics | PyTorch Docs
https://huggingface.co/docs/transformers/index | Transformers Overview | HuggingFace
https://towardsdatascience.com/attention-is-all-you-need | Attention Mechanism | Towards Data Science

# 4. Index them
python scripts/batch_index_urls.py --file job_specific_urls.txt --category job_prep
```

### **Pattern 2: Topic Deep Dive**

```bash
# Comprehensive resources for one topic

# Bayesian Statistics - urls.txt
https://towardsdatascience.com/bayesian-inference-intuition | Bayesian Intuition | Towards Data Science
https://stats.stackexchange.com/questions/2641/what-is-the-difference | Likelihood vs Probability | Cross Validated
https://arbital.com/p/bayes_rule | Bayes Rule Explained | Arbital
https://seeing-theory.brown.edu/bayesian-inference | Interactive Bayesian | Seeing Theory

python scripts/batch_index_urls.py --file bayesian_urls.txt
```

### **Pattern 3: Curated Learning Path**

```bash
# Build your own curriculum from web resources

# Week 1: Foundations
https://course.fast.ai/videos/?lesson=1 | Neural Network Basics | Fast.ai
# Week 2: CNNs
https://cs231n.github.io/convolutional-networks/ | CNNs Explained | Stanford CS231n
# Week 3: Transformers
https://jalammar.github.io/illustrated-transformer/ | Illustrated Transformer | Jay Alammar

python scripts/batch_index_urls.py --file curriculum_urls.txt
```

---

## 🐛 Troubleshooting

### **"Failed to extract content"**

**Problem**: Site blocks scraping or uses JavaScript

**Solution**:
```bash
# Try manual HTML download
curl -A "Mozilla/5.0" https://example.com/article > article.html

# Then index as local file (TODO: add HTML file indexer)
```

### **"Content is too short"**

**Problem**: Extracted only navigation/headers, not main content

**Solution**: Inspect page structure and adjust selectors in `index_web_resource.py`:
```python
# Current (generic):
main_content = soup.find('main') or soup.find('article')

# Custom (for specific site):
main_content = soup.find('div', class_='post-content')
```

### **"Duplicate content detected"**

**Problem**: Same URL indexed twice

**Solution**: Pinecone will update existing vectors, not create duplicates. Safe to re-run.

### **"Rate limited / 429 error"**

**Problem**: Too many requests to same domain

**Solution**:
```bash
# Increase delay in batch_index_urls.py
time.sleep(10)  # Wait 10 seconds between requests
```

---

## 📈 Best Practices

### **1. Quality over Quantity**
- 10 high-quality articles > 100 low-quality ones
- Prioritize authoritative sources (academic, official docs)

### **2. Topic-Source Mapping**
```
# Good: Specific topic from article
Maximum Likelihood Estimation

# Bad: Too generic
Statistics
```

### **3. Organize by Category**
```bash
# Separate categories for different domains
--category statistics
--category machine_learning
--category trading
```

### **4. Test Coverage**
After indexing, verify topics are discoverable:
```bash
python -c "
from app.services.learning_path_service import learning_path_service

coverage = learning_path_service.check_topic_coverage('Your Topic')
print(f'Covered: {coverage['covered']}')
print(f'Confidence: {coverage['confidence']:.3f}')
print(f'Source: {coverage.get('source', 'N/A')}')
"
```

### **5. Update Regularly**
```bash
# Keep a master URLs file and re-index periodically
# Web content gets updated, embeddings stay current

# Monthly refresh
python scripts/batch_index_urls.py --file master_urls.txt
```

---

## 🎯 Complete Example Workflow

### **Scenario: Preparing for Quant Trading Interview**

```bash
# 1. Create topic-specific URLs file
cat > quant_trading_urls.txt << 'EOF'
# Algorithmic Trading Basics
https://www.investopedia.com/terms/a/algorithmictrading.asp | Algorithmic Trading Overview | Investopedia
https://towardsdatascience.com/algorithmic-trading-with-python | Python for Trading | Towards Data Science

# Statistical Arbitrage
https://quantivity.wordpress.com/2009/11/09/statistical-arbitrage | Statistical Arbitrage Intro | Quantivity
https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1153505 | Pairs Trading Research | SSRN

# Risk Management
https://www.risk.net/derivatives/7654321/var-explained | Value at Risk | Risk.net
https://towardsdatascience.com/portfolio-optimization | Portfolio Optimization | Towards Data Science
EOF

# 2. Index all URLs
cd /home/user/Quants_Learn/backend
python scripts/batch_index_urls.py --file quant_trading_urls.txt --category trading

# 3. Verify indexing
python -c "
from app.services.vector_store import vector_store

topics = ['algorithmic trading', 'statistical arbitrage', 'value at risk']
for topic in topics:
    results = vector_store.search(topic, top_k=3)
    print(f'\n{topic}:')
    for r in results[:2]:
        print(f'  {r['score']:.3f} - {r['metadata']['source']}')
"

# 4. Start app and paste job description
python app/main.py

# Job description will now match against:
# - Your indexed PDFs (from index_document.py)
# - Your indexed web resources (from batch_index_urls.py)
# - Content generated using both sources
```

---

## 📚 Resources

- **Original script**: `backend/scripts/index_web_resource.py`
- **Batch script**: `backend/scripts/batch_index_urls.py`
- **URLs template**: `backend/scripts/index_urls.txt`
- **Main guide**: `CONTENT_GUIDE.md`

---

## 🔄 Integration with Workflow

```
PDF Documents        Web Resources
(confidential)       (public articles)
      ↓                    ↓
index_document.py    batch_index_urls.py
      ↓                    ↓
      └──── Pinecone ─────┘
              ↓
       Job Description
              ↓
       Topic Extraction
              ↓
       Coverage Check
       (searches both PDFs and web resources)
              ↓
       Claude Content Generation
       (uses chunks from both sources)
```

**Your content now comes from:**
1. ✅ Confidential PDFs (local only, indexed to Pinecone)
2. ✅ Public web articles (no files, indexed to Pinecone)
3. ✅ Both used together for comprehensive coverage

---

**Ready to use! Start indexing web resources universally.** 🚀
