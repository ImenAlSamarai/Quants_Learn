# Testing Smart Cache System - Automatic Learning Structure Generation

This guide explains how to test the automatic, cache-first learning structure generation system.

## Overview

The system automatically generates and caches learning structures (weeks/sections) when a user submits a job description:

1. **First Request**: Topic detected → Check cache → Cache MISS → Generate with GPT-4o-mini + RAG (~$0.006) → Cache result
2. **Subsequent Requests**: Topic detected → Check cache → Cache HIT → Retrieve instantly (FREE!)

This works transparently during the learning path generation flow - **no manual scripts required**.

## Prerequisites

### 1. Set Up Environment Variables

Copy the example environment file and fill in your API keys:

```bash
cd backend
cp .env.example .env
```

Edit `.env` and add your actual API keys:
```bash
OPENAI_API_KEY=sk-...  # Your OpenAI API key
PINECONE_API_KEY=...   # Your Pinecone API key
```

**Important**: Verify that `OPENAI_MODEL=gpt-4o-mini` (cost-effective model for generation)

### 2. Initialize Database

The `topic_structures` table has already been created. Verify it exists:

```bash
cd backend
python scripts/init_database.py
```

You should see:
```
✅ Database initialized successfully!
Created tables:
  - topic_structures (NEW - for caching learning structures)
```

### 3. Index Books (Optional)

If you haven't already indexed your books, run:

```bash
cd backend
python scripts/index_document.py ../content/finance/Advances_in_Financial_Machine_Learning.pdf
# Repeat for other books...
```

## Testing the Automatic Caching System

### Test 1: First-Time Generation (Cache MISS)

1. Start the backend server:
```bash
cd backend
python -m app.main
```

2. Submit a job description via API (using curl or Postman):

```bash
curl -X POST "http://localhost:8000/api/users/generate-path" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_1",
    "job_description": "Quantitative Researcher position requiring expertise in algorithmic trading strategies, statistical modeling, machine learning for alpha generation, risk management, and backtesting frameworks. Must have strong Python skills and experience with market microstructure."
  }'
```

3. **Expected Output (Console Logs)**:

Watch the backend console for these messages:

```
🔄 Auto-generating learning structures for covered topics (cache-first)...

[1/8] Processing: algorithmic strategies
   🔄 Cache MISS for 'algorithmic strategies' - generating with gpt-4o-mini...
   ✅ Generated and cached (4 weeks, 12 sections, ~$0.006)

[2/8] Processing: statistical modeling
   🔄 Cache MISS for 'statistical modeling' - generating with gpt-4o-mini...
   ✅ Generated and cached (3 weeks, 9 sections, ~$0.006)

[3/8] Processing: machine learning techniques
   🔄 Cache MISS for 'machine learning techniques' - generating with gpt-4o-mini...
   ✅ Generated and cached (5 weeks, 15 sections, ~$0.006)

...
```

4. **Verify Response Includes Learning Structures**:

The API response should include `learning_structure` for each covered topic:

```json
{
  "covered_topics": [
    {
      "topic": "algorithmic strategies",
      "learning_structure": {
        "weeks": [
          {
            "weekNumber": 1,
            "title": "Introduction to Algorithmic Trading",
            "sections": [...]
          }
        ],
        "estimated_hours": 20,
        "difficulty_level": 3,
        "cached": false  // ← First generation
      }
    }
  ]
}
```

### Test 2: Cache Retrieval (Cache HIT)

1. **Submit the SAME job description again** (or a different job mentioning the same topics):

```bash
curl -X POST "http://localhost:8000/api/users/generate-path" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_2",  // Different user!
    "job_description": "Senior Quant Trader role focused on algorithmic strategies and statistical arbitrage..."
  }'
```

2. **Expected Output (Console Logs)**:

```
🔄 Auto-generating learning structures for covered topics (cache-first)...

[1/5] Processing: algorithmic strategies
   ✅ Cache HIT for 'algorithmic strategies' (accessed 2 times)  // ← Instant retrieval!

[2/5] Processing: statistical modeling
   ✅ Cache HIT for 'statistical modeling' (accessed 2 times)

...
```

3. **Verify Cached Flag**:

```json
{
  "learning_structure": {
    "cached": true  // ← Retrieved from cache (FREE!)
  }
}
```

### Test 3: Direct Topic Structure API

You can also retrieve cached structures directly:

```bash
curl "http://localhost:8000/api/users/topics/algorithmic%20strategies/structure?keywords=trading%20algorithms,TWAP,VWAP"
```

**Expected Response**:
```json
{
  "weeks": [...],
  "estimated_hours": 20,
  "difficulty_level": 3,
  "source_books": [...],
  "cached": true
}
```

## Verification Checklist

- [ ] Database table `topic_structures` exists
- [ ] First job submission: console shows "Cache MISS" + generation messages
- [ ] First job response: `"cached": false` in learning_structure
- [ ] Second job submission: console shows "Cache HIT" + access count
- [ ] Second job response: `"cached": true` in learning_structure
- [ ] Different users with overlapping topics benefit from same cache
- [ ] No manual scripts needed - everything automatic!

## Inspecting the Cache Database

Check what's been cached:

```bash
cd backend
python -c "
import os
os.environ['PINECONE_API_KEY'] = 'dummy'
os.environ['OPENAI_API_KEY'] = 'dummy'

from app.models.database import SessionLocal, TopicStructure

db = SessionLocal()
structures = db.query(TopicStructure).all()

print(f'\\nCached Structures: {len(structures)}\\n')
for s in structures:
    print(f'  Topic: {s.topic_name}')
    print(f'  Weeks: {len(s.weeks)}')
    print(f'  Access Count: {s.access_count}')
    print(f'  Model: {s.generation_model}')
    print(f'  Created: {s.created_at}')
    print()

db.close()
"
```

## Expected Cost Savings

| Scenario | Without Caching | With Smart Cache |
|----------|----------------|------------------|
| First user (8 topics) | ~$0.048 | ~$0.048 (same) |
| Second user (same topics) | ~$0.048 | **$0.00 (FREE!)** |
| 100 users (same topics) | ~$4.80 | **~$0.048 (99% savings!)** |

## Troubleshooting

### Issue: "TopicStructure table not found"
**Solution**: Run `python scripts/init_database.py`

### Issue: "Cache always shows MISS"
**Possible causes**:
1. Different keywords → different MD5 hash → different cache key
2. Database not persisting (check database connection)
3. `is_valid` flag set to False

**Debug**: Check the `topic_hash` being generated

### Issue: No console output
**Solution**: Ensure `DEBUG=True` in `.env` and check that print statements aren't being suppressed

## Architecture Flow

```
User submits job
    ↓
Topic extraction (LLM)
    ↓
For each covered topic:
    ├─→ Generate cache key: MD5(topic_name + keywords)
    ├─→ Query database: TopicStructure.filter(topic_hash == key)
    ├─→ If cached: Return structure (access_count++)
    └─→ If not cached:
        ├─→ RAG retrieval (top 10 chunks from Pinecone)
        ├─→ LLM generation (gpt-4o-mini + context)
        ├─→ Save to TopicStructure table
        └─→ Return structure
    ↓
Learning path response (with structures included)
```

## Success Criteria

✅ All covered topics have `learning_structure` in API response
✅ First request shows cache MISS + ~$0.006 cost per topic
✅ Subsequent requests show cache HIT + $0.00 cost
✅ Different users benefit from same cached structures
✅ No manual batch scripts needed - fully automatic!

## Next Steps

After validating the caching system:

1. **Frontend Integration**: Update frontend to display cached week/section structures
2. **Content Generation**: Implement similar caching for actual section content (not just structures)
3. **Cache Management**: Add admin endpoints for cache invalidation and regeneration
4. **Analytics**: Track cache hit rates and cost savings
