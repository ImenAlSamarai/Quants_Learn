# Exact Prompts Used for Content Generation

## Overview

Your platform uses **2 different prompts** for **2 different stages** of content generation:

1. **GPT-4o-mini**: Topic structure generation (cheap, outline only)
2. **Claude Sonnet 3.5 / GPT-4 Turbo**: Section content generation (expensive, detailed content)

---

## Prompt 1: Topic Structure Generation (GPT-4o-mini)

**Location:** `learning_path_service.py:1295-1345`

**Model:** `gpt-4o-mini`
**Temperature:** `0.3`
**Max Tokens:** `2500`
**Cost:** ~$0.002 per topic

### System Prompt

```
You are an expert curriculum designer for quantitative finance education.
Create a structured learning roadmap (weeks → sections) for interview preparation.

CRITICAL REQUIREMENTS:
1. Structure into 2-4 weeks of learning
2. Each week has 2-4 sections
3. Each section is a focused sub-topic (45-90 min of study)
4. Base structure on PROVIDED BOOK CONTENT - don't invent topics not in the books
5. Order sections from foundational → advanced
6. Include practical examples and interview relevance

QUALITY STANDARDS - Section Titles Must Be SPECIFIC:
✅ GOOD: "Black-Scholes Formula Derivation", "Maximum Likelihood Estimation for Normal Distributions"
✅ GOOD: "Ridge vs Lasso: L1 vs L2 Regularization", "ARIMA Models for Financial Time Series"
❌ BAD: "Introduction to...", "Basics of...", "Overview of...", "Fundamentals"
❌ BAD: Generic topic names without specifics

Use concrete mathematical formulas, algorithm names, and specific techniques from the book content.
Make section titles immediately actionable and interview-focused.

Return ONLY valid JSON (no markdown, no extra text):
{
  "weeks": [
    {
      "weekNumber": 1,
      "title": "Week title",
      "sections": [
        {
          "id": "1.1",
          "title": "Section title",
          "topics": ["Key concept 1", "Key concept 2", "Key concept 3"],
          "estimatedMinutes": 60,
          "interviewRelevance": "Why this appears in interviews"
        }
      ]
    }
  ],
  "estimated_hours": 20,
  "difficulty_level": 3
}
```

### User Prompt

```
Topic: {topic_name}
Keywords: {keywords}
Source Books: {books_list}

Book Content (use this to structure your roadmap):
{context_text from RAG - top 20 chunks from books/web}

Create a practical learning roadmap for someone preparing for quant interviews.
Focus on concepts actually covered in the provided book content.
Return valid JSON only.
```

### Example Input

```
Topic: Maximum Likelihood Estimation
Keywords: MLE, likelihood function, parameter estimation, optimization
Source Books: Quant Learning Materials: Statistics, Elements of Statistical Learning

Book Content (use this to structure your roadmap):
Maximum likelihood estimation (MLE) is a method for estimating the parameters
of a probability distribution by maximizing a likelihood function...

[15-20 more chunks from books/web]

Create a practical learning roadmap for someone preparing for quant interviews.
Focus on concepts actually covered in the provided book content.
Return valid JSON only.
```

### Example Output

```json
{
  "weeks": [
    {
      "weekNumber": 1,
      "title": "Foundations of Maximum Likelihood",
      "sections": [
        {
          "id": "1.1",
          "title": "The Likelihood Function and Log-Likelihood",
          "topics": ["probability distributions", "joint likelihood", "logarithm properties"],
          "estimatedMinutes": 60,
          "interviewRelevance": "Fundamental concept tested in 90% of quant interviews"
        },
        {
          "id": "1.2",
          "title": "Deriving MLE for Normal Distribution",
          "topics": ["calculus optimization", "first-order conditions", "Gaussian parameters"],
          "estimatedMinutes": 75,
          "interviewRelevance": "Most common MLE derivation asked on whiteboards"
        }
      ]
    },
    {
      "weekNumber": 2,
      "title": "Properties and Applications",
      "sections": [
        {
          "id": "2.1",
          "title": "Asymptotic Properties: Consistency and Efficiency",
          "topics": ["consistency", "efficiency", "asymptotic normality"],
          "estimatedMinutes": 90,
          "interviewRelevance": "Advanced questions test understanding of statistical properties"
        }
      ]
    }
  ],
  "estimated_hours": 18,
  "difficulty_level": 3
}
```

---

## Prompt 2: Section Content Generation (Claude/GPT-4)

**Location:** `llm_service.py:510-579`

**Model:** `claude-3-5-sonnet-20241022` (primary) or `gpt-4-turbo-preview` (fallback)
**Temperature:** `0.7`
**Max Tokens:** `4000` (Claude) / `3000` (GPT-4)
**Cost:** ~$0.087 per section (Claude) / ~$0.18 per section (GPT-4)

### System Prompt (Same for both Claude and GPT-4)

```
You are an elite educator specializing in quantitative finance, with deep expertise in mathematics, statistics, and trading.

Your task is to create comprehensive, rigorous learning content for quant interview preparation.

CRITICAL: You MUST return VALID JSON in this EXACT structure (no markdown, no ```json wrapper):

{
  "introduction": "2-3 sentences introducing the concept, its importance in quant interviews, and why mastering it matters. Be direct and substantive.",
  "sections": [
    {
      "title": "Specific concept name (e.g., 'The OLS Problem', 'Deriving the Estimator')",
      "content": "Detailed explanation with LaTeX math. Use $...$ for inline math and $$...$$ for display equations. Include step-by-step derivations, bullet points for clarity, and concrete examples.",
      "keyFormula": "Main formula if applicable (e.g., '\\hat{\\beta} = (X^TX)^{-1}X^Ty')"
    }
  ],
  "keyTakeaways": [
    "Concise bullet point with key insight, can include LaTeX like $E[X] = \\mu$",
    "Another critical point interviewers expect you to know",
    "Third essential concept"
  ],
  "interviewTips": [
    "Practical interview advice (e.g., 'Be ready to derive on whiteboard in <5 min')",
    "Common pitfalls or what interviewers look for",
    "Connection to practical applications"
  ],
  "practiceProblems": [
    {
      "id": 1,
      "difficulty": "Easy",
      "text": "Specific problem with LaTeX if needed"
    },
    {
      "id": 2,
      "difficulty": "Medium",
      "text": "More challenging problem"
    }
  ],
  "resources": [
    {
      "source": "Book name from context",
      "chapter": "Specific chapter/section",
      "pages": "Page numbers if mentioned"
    }
  ]
}

QUALITY STANDARDS (Match validated "Statistical Modeling" example):
- Introduction: Direct, no filler. Immediately state why this matters for interviews
- Sections: 2-4 detailed sections with mathematical rigor
- LaTeX: Use proper notation: $inline$ and $$display$$ (escape backslashes: \\)
- Key Formulas: Highlight THE formula to memorize
- Interview Tips: Practical, specific advice
- Practice Problems: 2-3 problems of increasing difficulty
- Resources: Extract from provided book content

CRITICAL:
- Return ONLY valid JSON (no markdown wrapper, no extra text)
- Use \\  (double backslash) for LaTeX in JSON strings
- Draw heavily from provided book content
- Be mathematically rigorous but interview-focused
```

### User Prompt (Same for both Claude and GPT-4)

```
Topic: {topic_name}
Section {section_id}: {section_title}

Book Content to Incorporate:
{context_text from RAG - top 15 chunks from books/web}

Generate content matching the EXACT JSON structure specified in the system prompt.
This content will be used by candidates preparing for quant interviews at top firms.

Return ONLY the JSON object - no markdown formatting, no ```json wrapper, just the raw JSON.
```

### Example Input

```
Topic: Maximum Likelihood Estimation
Section 1.1: The Likelihood Function and Log-Likelihood

Book Content to Incorporate:
The likelihood function L(θ|x) represents the probability of observing data x given
parameters θ. For independent observations, L(θ) = ∏ᵢ p(xᵢ|θ)...

The log-likelihood ℓ(θ) = log L(θ) = ∑ᵢ log p(xᵢ|θ) is often easier to work with...

[12-15 more chunks from books/web including:
- Properties of likelihood
- Why log is used
- Optimization techniques
- Examples with normal distribution
- Innovation options web content about estimation
]

Generate content matching the EXACT JSON structure specified in the system prompt.
This content will be used by candidates preparing for quant interviews at top firms.

Return ONLY the JSON object - no markdown formatting, no ```json wrapper, just the raw JSON.
```

### Example Output (What Claude/GPT-4 Returns)

```json
{
  "introduction": "The likelihood function is the cornerstone of maximum likelihood estimation, quantifying how probable observed data is under different parameter values. In quant interviews, understanding the likelihood function and its logarithmic transformation is essential—it appears in everything from parameter estimation to model comparison. Mastering this concept enables you to derive estimators on the spot and explain why certain statistical methods work.",

  "sections": [
    {
      "title": "The Likelihood Function: Definition and Intuition",
      "content": "Given a parametric model with parameter vector $\\theta$ and independent observations $x_1, x_2, ..., x_n$, the **likelihood function** is defined as:\n\n$$L(\\theta | x_1,...,x_n) = \\prod_{i=1}^{n} f(x_i | \\theta)$$\n\nwhere $f(x_i | \\theta)$ is the probability density (or mass) function. The likelihood represents the probability of observing our data given specific parameter values.\n\n**Key Insight:** We're treating $\\theta$ as variable and data as fixed—opposite of probability!\n\n**Example:** For coin flips with unknown heads probability $p$, if we observe 7 heads in 10 flips:\n$$L(p|7H, 3T) = \\binom{10}{7}p^7(1-p)^3$$\n\nThe MLE is the value of $p$ that maximizes this function.",
      "keyFormula": "L(\\theta | x) = \\prod_{i=1}^{n} f(x_i | \\theta)"
    },
    {
      "title": "Log-Likelihood: Why Logarithms Matter",
      "content": "The **log-likelihood** is simply the natural logarithm of the likelihood:\n\n$$\\ell(\\theta) = \\log L(\\theta) = \\sum_{i=1}^{n} \\log f(x_i | \\theta)$$\n\n**Why use logarithms?**\n- **Numerical stability:** Products of small probabilities → underflow; sums are stable\n- **Easier optimization:** Sum is easier to differentiate than product\n- **Monotonicity:** $\\log$ is monotone increasing, so $\\arg\\max L(\\theta) = \\arg\\max \\ell(\\theta)$\n\n**Practical Example:** For $n=1000$ observations from $N(0,1)$, likelihood involves $10^{-434}$ scale numbers—completely unusable! Log-likelihood stays in manageable range.\n\n**Interview Tip:** Always work with log-likelihood in practice. If asked to maximize likelihood, immediately take logs.",
      "keyFormula": "\\ell(\\theta) = \\sum_{i=1}^{n} \\log f(x_i | \\theta)"
    },
    {
      "title": "Finding the MLE: Optimization Mechanics",
      "content": "To find the maximum likelihood estimator $\\hat{\\theta}_{MLE}$:\n\n**Step 1: Take derivative** (score function)\n$$S(\\theta) = \\frac{\\partial \\ell(\\theta)}{\\partial \\theta}$$\n\n**Step 2: Set equal to zero** (first-order condition)\n$$S(\\hat{\\theta}) = 0$$\n\n**Step 3: Verify it's a maximum** (check second derivative < 0)\n$$\\frac{\\partial^2 \\ell(\\theta)}{\\partial \\theta^2} < 0$$\n\n**Example: Normal distribution MLE**\nFor $X_i \\sim N(\\mu, \\sigma^2)$:\n$$\\ell(\\mu, \\sigma^2) = -\\frac{n}{2}\\log(2\\pi\\sigma^2) - \\frac{1}{2\\sigma^2}\\sum_{i=1}^n(x_i-\\mu)^2$$\n\nSolving $\\frac{\\partial \\ell}{\\partial \\mu} = 0$ yields:\n$$\\hat{\\mu}_{MLE} = \\frac{1}{n}\\sum_{i=1}^n x_i = \\bar{x}$$\n\nThe sample mean is the MLE for $\\mu$!",
      "keyFormula": "\\frac{\\partial \\ell(\\theta)}{\\partial \\theta} = 0"
    }
  ],

  "keyTakeaways": [
    "Likelihood $L(\\theta|x)$ treats parameters as variable and data as fixed—opposite of probability $P(x|\\theta)$",
    "Always use log-likelihood $\\ell(\\theta) = \\log L(\\theta)$ in practice for numerical stability and easier calculus",
    "MLE is found by maximizing likelihood: solve $\\frac{\\partial \\ell}{\\partial \\theta} = 0$ and verify second derivative < 0",
    "For i.i.d. data, likelihood factors: $L(\\theta) = \\prod_i f(x_i|\\theta)$ becomes $\\ell(\\theta) = \\sum_i \\log f(x_i|\\theta)$",
    "The MLE for normal distribution mean is the sample mean $\\bar{x}$—an intuitive and frequently tested result"
  ],

  "interviewTips": [
    "Be ready to derive the MLE for normal distribution parameters in <5 minutes on a whiteboard—this is the #1 most common MLE derivation in interviews",
    "When asked 'why use log-likelihood?', mention BOTH numerical stability AND ease of differentiation (products → sums)",
    "Interviewers test if you understand the conceptual flip: likelihood treats θ as variable, probability treats x as variable",
    "Common trap: forgetting to verify the second derivative is negative. Always mention checking it's a maximum, not minimum",
    "Connect to trading: MLE is used daily for calibrating volatility models, estimating factor exposures, and fitting distributions to returns"
  ],

  "practiceProblems": [
    {
      "id": 1,
      "difficulty": "Easy",
      "text": "Derive the MLE for the parameter λ of an exponential distribution Exp(λ) based on n i.i.d. samples. Show all steps including taking the log-likelihood and solving the first-order condition."
    },
    {
      "id": 2,
      "difficulty": "Medium",
      "text": "You observe returns r₁, r₂, ..., r₁₀₀ from a normal distribution N(μ, σ²). Derive the MLE for both μ and σ² simultaneously. Explain why the MLE for σ² is biased and how to correct it."
    },
    {
      "id": 3,
      "difficulty": "Hard",
      "text": "Consider a mixture model: X ~ 0.6·N(0,1) + 0.4·N(3,1). Given 50 samples, explain why MLE is difficult here and describe the EM algorithm approach to find MLEs for mixture weights and component parameters."
    }
  ],

  "resources": [
    {
      "source": "Quant Learning Materials: Statistics",
      "chapter": "Chapter 4: Maximum Likelihood Estimation",
      "pages": "89-112"
    },
    {
      "source": "Elements of Statistical Learning",
      "chapter": "Chapter 2: Overview of Supervised Learning",
      "pages": "21-24"
    }
  ]
}
```

---

## API Call Parameters

### GPT-4o-mini (Topic Structure)

```python
response = self.llm_service.client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ],
    temperature=0.3,        # Low temp for consistency
    max_tokens=2500,        # Enough for outline
    response_format={"type": "json_object"}  # Ensures valid JSON
)
```

### Claude Sonnet 3.5 (Section Content)

```python
response = self.claude_client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=4000,        # More tokens for detailed content
    temperature=0.7,        # Higher temp for creative explanations
    system=system_prompt,
    messages=[{
        "role": "user",
        "content": user_prompt
    }]
)
```

### GPT-4 Turbo (Fallback)

```python
response = self.client.chat.completions.create(
    model="gpt-4-turbo-preview",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ],
    temperature=0.7,
    max_tokens=3000,
    response_format={"type": "json_object"}
)
```

---

## Key Differences Between Prompts

### Topic Structure Prompt (GPT-4o-mini)

**Purpose:** Generate outline only
**Focus:** Structure and organization
**Output:** Weeks, sections, titles, time estimates
**Content Depth:** Minimal (just titles and metadata)
**RAG Chunks:** 20 chunks
**Cost:** Very cheap (~$0.002)

### Section Content Prompt (Claude/GPT-4)

**Purpose:** Generate full educational content
**Focus:** Detailed explanations, derivations, examples
**Output:** Introduction, detailed sections with LaTeX, takeaways, tips, problems, resources
**Content Depth:** Maximum (full teaching content)
**RAG Chunks:** 15 chunks
**Cost:** Expensive (~$0.087 with Claude)

---

## Why Two Different Prompts?

**Cost Optimization:**
- Don't waste Claude's expensive tokens on simple outlines
- Use cheap model for structure, premium model for content

**Quality Optimization:**
- GPT-4o-mini is perfect for JSON structure generation
- Claude Sonnet 3.5 is best for mathematical explanations and teaching

**Separation of Concerns:**
- Structure generation doesn't need deep knowledge
- Content generation needs expert-level explanation ability

---

## Prompt Engineering Techniques Used

### 1. **Explicit JSON Structure**
Both prompts include the EXACT JSON structure expected, reducing parsing errors.

### 2. **Quality Examples**
"✅ GOOD" and "❌ BAD" examples teach the model what quality looks like.

### 3. **Concrete Instructions**
"2-4 weeks", "45-90 min", "$...$" for inline math—specific, not vague.

### 4. **RAG Context Integration**
Both prompts include "Book Content to Incorporate" to ground responses in actual sources.

### 5. **Interview Focus**
Repeatedly emphasizes "interview preparation", "quant interviews", "whiteboard derivations".

### 6. **LaTeX Formatting**
Explicit instructions for LaTeX syntax ($...$, $$...$$, double backslashes).

### 7. **Validation Reference**
"Match validated 'Statistical Modeling' example" grounds quality in a known good output.

---

## Summary

**Your platform uses well-engineered prompts that:**
- ✅ Optimize cost (cheap for structure, premium for content)
- ✅ Optimize quality (best model for each task)
- ✅ Ground in sources (RAG chunks from books/web)
- ✅ Enforce structure (explicit JSON schemas)
- ✅ Focus on interviews (practical, actionable content)
- ✅ Include quality controls (examples, validation references)

**These are production-quality prompts!** They show attention to:
- Token efficiency
- Output consistency
- Mathematical rigor
- Practical application
- Cost management

No wonder your content generation costs ~$0.87 per topic but delivers high-quality, interview-focused learning materials.
