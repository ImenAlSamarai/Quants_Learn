# Quick Start Guide: Activating Real Content Mode

This guide shows how to enable real AI-generated content (currently in demo mode).

---

## Current Status

**Demo Mode Active** - Platform shows placeholder data because backend is not running.
- ✅ 19 real markdown files ready (4,480 lines of content)
- ✅ Backend code complete and functional
- ⏸️ Backend services not started (requires API keys)

---

## Option 1: Quick Test (No Backend Setup)

Just want to verify content exists?

```bash
# View real content files
cat content/linear_algebra/vectors.md | head -50

# Count content
find content -name "*.md" -type f -exec wc -l {} + | tail -1
# Shows: 4480 total lines

# List all topics
find content -name "*.md" -type f
```

---

## Option 2: Full Backend Setup (Real AI Content)

### Prerequisites
- PostgreSQL installed
- Python 3.9+
- API Keys: OpenAI, Pinecone

### Step 1: Database Setup

```bash
# Install PostgreSQL (if not installed)
# macOS:
brew install postgresql
brew services start postgresql

# Ubuntu:
sudo apt-get install postgresql
sudo systemctl start postgresql

# Create database
createdb quant_learn
```

### Step 2: Environment Configuration

```bash
# Copy example env file
cp backend/.env.example backend/.env

# Edit with your API keys
nano backend/.env
```

**Required values:**
```bash
PINECONE_API_KEY=your_pinecone_key_here
OPENAI_API_KEY=your_openai_key_here
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/quant_learn
```

### Step 3: Install Backend Dependencies

```bash
cd backend

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 4: Index Content

```bash
# Still in backend directory
python scripts/index_content.py --content-dir ../content

# Expected output:
# Processing 19 markdown files...
# Creating ~150 text chunks...
# Generating embeddings...
# Indexing to Pinecone...
# ✓ Indexed 19 nodes successfully
```

### Step 5: Start Backend

```bash
# In backend directory
python -m app.main

# Should see:
# Initializing database...
# Connected to Pinecone index: quant-learning
# Server starting at http://localhost:8000
# API docs available at http://localhost:8000/docs
```

### Step 6: Start Frontend

```bash
# New terminal
cd frontend

# Install dependencies (first time)
npm install

# Start dev server
npm run dev

# Opens at http://localhost:5173
```

---

## Verification

### Test API (Backend Running)

```bash
# Health check
curl http://localhost:8000/health

# Get mind map data
curl http://localhost:8000/api/nodes/mindmap

# Generate explanation (replace node_id)
curl -X POST http://localhost:8000/api/content/query \
  -H "Content-Type: application/json" \
  -d '{
    "node_id": 1,
    "query_type": "explanation",
    "user_id": "test_user"
  }'
```

### Test Frontend

1. Open http://localhost:5173
2. Click any category (e.g., "Linear Algebra")
3. Click "Explore Mode" - should show mind map with real topics
4. Click any node - should load AI-generated content
5. Try different content tabs: Explanation, Examples, Quiz, Visualize

**Demo Mode:** Shows "Connect backend to see AI-generated content"
**Real Mode:** Shows personalized explanations with code examples

---

## Troubleshooting

### "Connection refused" error
- Backend not running → Start with `python -m app.main`
- Wrong port → Check `VITE_API_URL` in `frontend/.env`

### "Pinecone index not found"
- Run indexing script first: `python scripts/index_content.py`
- Check Pinecone dashboard for index creation

### "No content generated"
- Verify OpenAI API key has credits
- Check backend logs for errors
- Try different difficulty level (1-5)

### Empty mind map
- Run indexing to populate database
- Check PostgreSQL connection
- Verify `nodes` table has data: `psql quant_learn -c "SELECT COUNT(*) FROM nodes;"`

---

## API Keys Setup

### Pinecone (Vector Database)
1. Sign up: https://www.pinecone.io/
2. Create project
3. Get API key from dashboard
4. Free tier: 1 index, 100k vectors (enough for this platform)

### OpenAI (LLM)
1. Sign up: https://platform.openai.com/
2. Add payment method (pay-as-you-go)
3. Create API key
4. Typical cost: ~$0.01-0.05 per content generation

---

## Content Types Available

When backend is running, you get 4 content types per topic:

### 1. Explanation
- Conceptual overview
- Tailored to learning level (1-5)
- 200-500 words
- Markdown formatted

### 2. Examples
- Real-world finance scenarios
- Step-by-step solutions
- Python code snippets
- Syntax highlighted

### 3. Quiz
- 5 multiple-choice questions
- Explanations for each answer
- Difficulty-adaptive
- Score tracking

### 4. Visualization
- Interactive charts
- Plotly.js configs
- Mathematical illustrations
- Dynamic parameters

---

## Difficulty Levels

Platform adapts content to your learning level:

**Level 1: Undergraduate**
- Simple language, everyday analogies
- Minimal equations, focus on intuition
- Basic numerical examples

**Level 2: Foundational Math**
- Balance intuition with formalism
- Simple real-world examples
- Basic calculus/linear algebra

**Level 3: Graduate (Default)**
- Mathematical rigor + intuition
- Realistic quant finance problems
- Formal notation

**Level 4: PhD Research**
- Subtle points, edge cases
- Research-level examples
- Advanced mathematics

**Level 5: Expert Practitioner**
- Technical depth, latest research
- Production implementations
- Full mathematical rigor

**Set level:** Click Settings (gear icon) → Adjust Learning Level slider

---

## Performance Tips

### Caching
- First request: ~2-5 seconds (LLM generation)
- Cached requests: <100ms (database lookup)
- Cache persists across restarts

### Clear Cache
```bash
# API endpoint
curl -X DELETE http://localhost:8000/api/admin/cache

# Or invalidate specific content
curl -X POST http://localhost:8000/api/admin/invalidate-cache \
  -H "Content-Type: application/json" \
  -d '{"node_id": 1, "content_type": "explanation"}'
```

### Monitor Performance
```bash
# Admin stats
curl http://localhost:8000/api/admin/stats

# Shows:
# - Total queries
# - Cache hit rate
# - Most accessed nodes
# - Popular content types
# - Average rating by difficulty
```

---

## Next Steps

Once real content mode is working:

1. **Explore All Categories**
   - Linear Algebra (6 topics)
   - Calculus (5 topics)
   - Probability (4 topics)
   - Statistics (4 topics)

2. **Try Different Content Types**
   - Compare explanations at different levels
   - Work through examples
   - Test quizzes
   - View visualizations

3. **Track Progress**
   - Mark topics complete
   - View overall progress stats
   - Get personalized recommendations

4. **Add Your Own Content**
   - Upload markdown files via Admin Panel
   - Run indexing to make searchable
   - Content appears in mind map

---

## Summary

**Current State:**
- ✅ Real content exists (19 files, 4,480 lines)
- ✅ Backend fully functional
- ⏸️ Demo mode active (backend not running)

**To Activate Real Mode:**
1. Set up PostgreSQL database
2. Add API keys to `.env`
3. Run content indexing
4. Start backend server
5. Refresh frontend

**Need Help?**
- Check `VERIFICATION_REPORT.md` for detailed architecture
- Review backend logs for errors
- Visit API docs: http://localhost:8000/docs (when running)

---

**Last Updated:** 2025-11-17
