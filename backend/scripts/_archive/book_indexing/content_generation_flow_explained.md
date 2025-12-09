# Content Generation Flow: Book Data vs LLM

## Your Question
"When does LLM get called vs using purely book data? What exactly is shown to users?"

---

## ANSWER: We ALWAYS Use Both (Book + LLM)

### Content Flow

```
User Opens Topic
      ↓
[1] RETRIEVE from Vector Store (Pinecone)
      ↓
    📚 Pure Book Content (chunks from Bouchaud Ch 1)
      ↓
[2] SEND to OpenAI LLM
      ↓
    🤖 LLM Synthesizes Explanation
      ↓
[3] DISPLAY to User
      ↓
    User Sees: LLM-generated content based on book
```

---

## Detailed Flow for "Lévy Distributions"

### Step 1: Content Stored (During Indexing)

```python
# When we index Bouchaud Ch 1.8:
content = """
1.8 Lévy distributions and Paretian tails

Lévy distributions appear naturally in the context of the CLT...
The tails of Lévy distributions are much 'fatter' than Gaussians...

L_μ(x) ~ μA_μ / |x|^(1+μ)  for x → ±∞
...
[2000 characters of mathematical content from book]
"""

# We split into chunks and store in vector store
chunks = split_text(content)  # → 15 chunks
vector_store.index(chunks, node_id=5, metadata={"source": "bouchaud_ch1"})
```

**Stored Data:**
- ✅ Exact text from Bouchaud book (in vector database)
- ✅ Embeddings for semantic search
- ❌ NOT shown directly to user

---

### Step 2: User Opens Topic (Frontend)

```javascript
// frontend/src/components/study/StudyMode.jsx
useEffect(() => {
  // User clicks "Lévy Distributions" topic
  const response = await queryContent(topic.id, 'explanation');
  setContent(response);
}, [topic.id]);
```

---

### Step 3: Backend Retrieves & Generates

```python
# backend/app/routes/content.py
@router.post("/query")
def query_content(request: QueryRequest):

    # [STEP A] Retrieve relevant chunks from vector store
    matches = vector_store.search(
        query="Lévy distributions",
        node_id=request.node_id,
        top_k=5  # Get top 5 most relevant chunks
    )

    # Extract book text from matches
    context_chunks = [match['text'] for match in matches]
    # → ["L_μ(x) ~ μA_μ...", "power-law behaviour...", "μ=2 Gaussian...", ...]

    # [STEP B] Send to LLM to synthesize
    generated_content = llm_service.generate_explanation(
        topic=node.title,
        context_chunks=context_chunks,  # Book content as context
        difficulty_level=user.learning_level
    )

    return QueryResponse(
        generated_content=generated_content,  # LLM output
        source_chunks=context_chunks[:200]    # Book snippets (for reference)
    )
```

---

### Step 4: LLM Synthesizes (OpenAI Call)

```python
# app/services/llm_service.py
def generate_explanation(topic, context_chunks, difficulty_level):

    prompt = f"""
    You are a quantitative finance educator.

    Topic: {topic}
    Difficulty Level: {difficulty_level}

    Context from book:
    {chr(10).join(context_chunks)}  # ← BOOK CONTENT HERE

    Generate a clear explanation that:
    1. Explains the concept intuitively
    2. Shows key formulas from the book
    3. Explains why this matters in finance
    4. Provides a simple example

    Use the book content as your source of truth.
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content
```

**What LLM Receives:**
```
Context from book:
1. L_μ(x) ~ μA_μ / |x|^(1+μ) for large x, where 0 < μ < 2...
2. For μ = 2, one recovers Gaussian. When μ decreases from 2...
3. An important consequence is that variance is formally infinite...
4. Truncated Lévy distributions account for exponential cut-off...
5. Power-law tails are useful for multiscale phenomena...
```

**What LLM Generates (Example):**
```markdown
# Lévy Distributions and Heavy Tails

## Why This Matters in Finance

Financial returns don't follow normal distributions. During market crashes,
extreme events occur far more frequently than Gaussian models predict. Lévy
distributions better capture this "fat-tailed" behavior.

## The Math (from Bouchaud)

Lévy distributions have power-law tails:

L_μ(x) ~ μA_μ / |x|^(1+μ)  for large x

where μ is the "tail parameter" (0 < μ < 2):
- μ = 2: Gaussian (normal market conditions)
- μ < 2: Fat tails (extreme events more likely)
- μ ≤ 1: Even the mean doesn't exist!

## Key Insight: Infinite Variance

When μ ≤ 2, the variance is formally infinite. This means:
- Standard deviation is mathematically undefined
- Traditional risk measures (like Sharpe ratio) break down
- You need different tools (like Expected Shortfall)

## Real-World Example

Black Monday (1987): Stock market dropped 22% in one day. Under Gaussian
assumptions, this was a 20+ sigma event (should happen once in 10^80 years).
Under Lévy distribution with μ = 1.7, this is a 4-sigma event (happens
every few decades) - much more realistic!

## Practical Application

Use truncated Lévy distributions when modeling:
- Stock returns (especially during crises)
- Commodity prices
- Credit default events
- Any market with "black swan" events
```

---

## What User Sees

### Main Content Panel:
```
┌─────────────────────────────────────────┐
│  📊 Lévy Distributions                  │
│  ───────────────────────────────────    │
│                                         │
│  [LLM-Generated Explanation]            │
│  - Why This Matters in Finance          │
│  - The Math (from Bouchaud)             │
│  - Key Insight: Infinite Variance       │
│  - Real-World Example                   │
│  - Practical Application                │
│                                         │
│  📚 Source: Bouchaud Ch 1.8            │
└─────────────────────────────────────────┘

[💡 Get AI Insights] ← Separate button
```

### "Get AI Insights" Button (Separate):
```
┌─────────────────────────────────────────┐
│  💡 Practitioner Insights               │
│  ───────────────────────────────────    │
│                                         │
│  When to Use:                           │
│  - During market stress periods         │
│  - When modeling tail risk              │
│                                         │
│  Limitations:                           │
│  - Assumes stationarity                 │
│  - Parameter estimation is difficult    │
│                                         │
│  Practical Tips:                        │
│  - Start with Student's t for easier    │
│    estimation                           │
│  - Use truncated Lévy for finite        │
│    variance                             │
└─────────────────────────────────────────┘
```

---

## Summary Table

| Component | Data Source | LLM Used? | When Generated? |
|-----------|-------------|-----------|-----------------|
| **Main Topic Content** | Book chunks → LLM synthesis | ✅ YES | On-demand (cached) |
| **"Get AI Insights" Button** | Pre-generated insights | ✅ YES | Pre-indexed (via scripts) |
| **Source Snippets** | Raw book text | ❌ NO | Retrieved from vector store |
| **Quiz Questions** | Book context → LLM generates | ✅ YES | On-demand |
| **Examples** | Book context → LLM generates | ✅ YES | On-demand |

---

## Why This Hybrid Approach?

### 🎯 Advantages:

1. **Accuracy**: Grounded in book content (not hallucinated)
2. **Clarity**: LLM explains complex math in accessible language
3. **Relevance**: Connects theory to practical finance applications
4. **Adaptability**: Adjusts explanation based on user level
5. **Examples**: LLM adds real-world context not in book

### Example Comparison:

**Pure Book Text** (what we DON'T show):
```
L_μ(x) ~ μA_μ/|x|^(1+μ) for x → ±∞, where 0 < μ < 2 is a certain
exponent (often called α), and A_μ± two constants which we call
tail amplitudes, or scale parameters...
```
❌ Too dense, no context, no finance application

**LLM Synthesis** (what we DO show):
```
Lévy distributions have "fat tails" meaning extreme events are much
more likely than in normal distributions. The parameter μ controls
how "fat" the tails are. When μ < 2, the variance is infinite -
this better matches real market behavior during crashes.

Real Example: Black Monday 1987...
```
✅ Clear, contextualized, with finance application

---

## For Statistics Enhancement

### When we add Bouchaud content to inference.md:

```
inference.md (existing)
    ↓
[Existing content already indexed]
    ↓
Add new sections from Bouchaud Ch 1
    ↓
Re-index entire inference.md to vector store
    ↓
User opens "Statistical Inference" topic
    ↓
Vector store retrieves relevant chunks:
  - Existing: Gaussian, CLT, MLE
  - NEW: Lévy distributions, heavy tails
    ↓
LLM synthesizes complete explanation:
  "Statistical inference deals with drawing conclusions from data.
   Most classical methods assume Gaussian distributions (CLT).
   However, financial data often has heavy tails (Lévy distributions)
   where variance may not exist. This changes how we..."
    ↓
User sees coherent explanation covering both old + new content
```

**Key Point:** Even though we're "enhancing" inference.md (not creating new topic),
the user still gets LLM-generated explanation based on the enhanced content.

---

## Configuration Options (Future)

We could add settings to let users choose:

```
┌─────────────────────────────────────────┐
│  ⚙️ Content Display Settings            │
│  ───────────────────────────────────    │
│                                         │
│  ○ LLM Explanation (recommended)        │
│  ○ Book Text Only                       │
│  ○ Both (LLM + raw book sections)       │
│                                         │
│  Difficulty: [Beginner ▸ Advanced]      │
└─────────────────────────────────────────┘
```

Currently: Always use LLM synthesis with book content as context.

