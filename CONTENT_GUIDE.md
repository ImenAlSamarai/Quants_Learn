# Content Management Guide

This guide explains how to add and manage learning materials (PDFs, documents, web resources) for Quants_Learn.

---

## 📁 Directory Structure

```
content/
├── confidential/          # 🔒 NOT committed to GitHub (gitignored)
│   ├── proprietary_research.pdf
│   └── firm_materials/
├── private/              # 🔒 NOT committed to GitHub (gitignored)
│   └── personal_notes.pdf
├── statistics/           # ✅ Public materials (committed)
│   ├── bouchaud_book.pdf
│   └── overview.md
├── machine_learning/     # ✅ Public materials
│   ├── elements_of_statistical_learning.pdf
│   └── deep_learning_foundations.pdf
└── probability/          # ✅ Public materials
    └── foundations.md
```

---

## 🔒 Handling Confidential Documents

### **Strategy 1: Use Dedicated Directories** (Recommended)

Place all confidential materials in `content/confidential/` or `content/private/`:

```bash
# These directories are automatically gitignored
content/confidential/
content/private/
```

**Example:**
```bash
# Add your proprietary materials
cp ~/Downloads/proprietary_research.pdf content/confidential/
cp ~/Downloads/firm_materials/*.pdf content/confidential/firm_materials/

# Index them normally (they'll be in Pinecone but NOT in GitHub)
python backend/scripts/index_content.py --content-dir content/confidential
```

### **Strategy 2: Use Naming Convention**

Name files with `_confidential`, `_private`, or `_internal` suffix:

```bash
# These patterns are gitignored
content/statistics/advanced_trading_confidential.pdf
content/research/internal_report_private.pdf
```

### **Strategy 3: Ignore All PDFs** (Nuclear Option)

If you want to gitignore ALL PDFs by default:

1. Edit `.gitignore`
2. Uncomment this line:
   ```
   content/**/*.pdf
   ```

---

## 🌐 Using Web Resources

### **Quick Example**

```bash
# Index a web article about statistical modeling
python backend/scripts/index_web_resource.py \
    --url "https://towardsdatascience.com/understanding-mle" \
    --topic "Maximum Likelihood Estimation" \
    --source-name "Towards Data Science" \
    --category "statistics"
```

### **Supported Web Sources**

✅ **Good sources:**
- Medium articles (Towards Data Science, Analytics Vidhya)
- Stack Exchange (stats.stackexchange.com, quant.stackexchange.com)
- Documentation sites (scikit-learn docs, PyTorch tutorials)
- Academic blogs (distill.pub, blog.ml.cmu.edu)
- ArXiv HTML papers

⚠️ **May have issues:**
- Sites with heavy JavaScript (React SPAs) - you may need Selenium
- Paywalled content (WSJ, Bloomberg Terminal)
- Sites with aggressive anti-scraping (LinkedIn, some research portals)

### **Advanced: Batch Index Multiple URLs**

Create a file `urls.txt`:
```
https://towardsdatascience.com/article1, Maximum Likelihood, Towards Data Science
https://stats.stackexchange.com/questions/12345, Bayesian Inference, Cross Validated
https://scikit-learn.org/stable/modules/linear_model.html, Linear Regression, Scikit-Learn Docs
```

Then index in batch:
```bash
while IFS=',' read -r url topic source; do
    python backend/scripts/index_web_resource.py \
        --url "$url" \
        --topic "$topic" \
        --source-name "$source"
done < urls.txt
```

---

## 📚 Indexing Documents

### **1. Index PDFs or Markdown Files**

```bash
# Index a single directory
python backend/scripts/index_content.py --content-dir content/statistics

# Index all content (including confidential - safe, won't commit)
python backend/scripts/index_content.py --content-dir content
```

### **2. Index Specific Chapter from Book**

Example scripts already exist for granular indexing:
```bash
# Index specific chapters
python backend/scripts/index_esl_chapter3.py      # Elements of Statistical Learning Ch3
python backend/scripts/index_dl_chapter10.py      # Deep Learning Foundations Ch10
```

You can create similar scripts for your confidential materials.

### **3. Check What's Indexed**

```python
# Query to see what's in Pinecone
from app.services.vector_store import vector_store

results = vector_store.query(
    query="maximum likelihood estimation",
    top_k=5,
    namespace="statistics"
)

for match in results:
    print(f"Source: {match['metadata']['source']}")
    print(f"Text: {match['metadata']['text'][:100]}...")
    print("---")
```

---

## ⚙️ Workflow Examples

### **Scenario 1: Adding Confidential Trading Strategy PDFs**

```bash
# 1. Create confidential directory
mkdir -p content/confidential/trading_strategies

# 2. Copy your PDFs
cp ~/secure_drive/proprietary_*.pdf content/confidential/trading_strategies/

# 3. Verify they're gitignored
git status  # Should NOT show these files

# 4. Index them (they go to Pinecone, not GitHub)
python backend/scripts/index_content.py \
    --content-dir content/confidential/trading_strategies
```

**Result:**
- ✅ Documents indexed in Pinecone (usable in RAG)
- ✅ NOT in GitHub (confidential)
- ✅ Only in your local machine + Pinecone cloud

### **Scenario 2: Using Online Tutorial as Learning Material**

```bash
# Index a web tutorial about Bayesian methods
python backend/scripts/index_web_resource.py \
    --url "https://towardsdatascience.com/bayesian-inference-101" \
    --topic "Bayesian Inference" \
    --source-name "Towards Data Science" \
    --category "statistics" \
    --subcategory "bayesian"
```

**Result:**
- ✅ Content extracted and indexed
- ✅ No files in git (just metadata in Pinecone)
- ✅ Available for RAG queries

### **Scenario 3: Preparing for a Job Interview**

```bash
# 1. Add firm-specific materials (confidential)
cp job_description.pdf content/confidential/
cp firm_research_reports/*.pdf content/confidential/firm_research/

# 2. Add public reference materials
cp textbooks/*.pdf content/machine_learning/

# 3. Index web resources mentioned in job posting
python backend/scripts/index_web_resource.py \
    --url "https://arxiv.org/html/2301.12345" \
    --topic "Transformer Models" \
    --source-name "ArXiv"

# 4. Index everything
python backend/scripts/index_content.py --content-dir content

# 5. Test with job description
python backend/app/main.py
# Then paste job description in UI
```

---

## 🔍 Verifying Gitignore Works

```bash
# Check git status - should NOT show confidential files
git status

# Check what files git tracks in content/
git ls-files content/

# If you see a confidential file, remove it from git:
git rm --cached content/confidential/sensitive.pdf
git commit -m "Remove confidential file from git history"
```

---

## 🛡️ Security Best Practices

1. **Never commit API keys or credentials**
   - Already handled in `.env` (gitignored)

2. **Use confidential/ or private/ directories**
   - Automatically gitignored
   - Still indexed to Pinecone (usable)

3. **Review before pushing**
   ```bash
   git status
   git diff --staged
   # Verify no confidential files listed
   ```

4. **Pinecone is private to your account**
   - Content indexed to Pinecone is NOT public
   - Only accessible with your API key
   - Safe for confidential materials

5. **If you accidentally commit confidential data**
   ```bash
   # Remove from current commit
   git rm --cached path/to/file
   git commit --amend

   # If already pushed, rewrite history (CAREFUL!)
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch path/to/file" \
     HEAD
   ```

---

## 📊 Current Status

Run this to see what's currently indexed:

```bash
# Check content directory
ls -R content/

# Check what git tracks
git ls-files content/

# Check Pinecone stats
python -c "from app.services.vector_store import vector_store; print(vector_store.index.describe_index_stats())"
```

---

## 🆘 Troubleshooting

### "Web scraping returns empty text"
- Site may use JavaScript rendering
- Try: `pip install selenium` and modify script to use Selenium WebDriver

### "PDF indexing fails"
- Ensure PDF is not password-protected
- Check file permissions: `chmod 644 file.pdf`

### "Accidentally committed confidential file"
- See "Security Best Practices" → section 5 above

### "Want to share some but not all PDFs"
- Move public PDFs to topic directories (e.g., `content/statistics/`)
- Move confidential ones to `content/confidential/`
- Git will only track the public ones

---

## 📧 Questions?

Check existing scripts:
```bash
ls backend/scripts/index_*.py
```

Most common patterns already have examples!
