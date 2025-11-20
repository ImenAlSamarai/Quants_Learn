# Statistics Learning Paths Configuration

## Current State (PROBLEM!)

Currently, Statistics topics do NOT have learning paths configured.

### What User Sees Now (Difficulty-Based Grouping):

```
Statistics Category Sidebar:
├── 📊 Difficulty 2 (Beginner/Intermediate)
│   ├── Statistics (overview)
│   └── Statistical Inference
│
└── 📈 Difficulty 3 (Advanced)
    ├── Regression Analysis
    └── Time Series Analysis
```

**Problem**: This is the OLD organizational structure (Core concepts, Intermediate, Advanced) that you mentioned we should replace with optimal learning paths!

---

## Proposed Solution: Statistics Learning Paths

Based on our hybrid enhancement strategy, here's the optimal learning path organization:

### Recommended Learning Paths for Statistics:

```yaml
statistics_paths:

  # Path 1: Foundational Inference (Start here)
  foundational_inference:
    name: "Statistical Inference & Distributions"
    description: "⭐ Start here - Core statistical methods"
    color: "#10b981"  # green
    icon: "📊"
    sequence: 1
    topics:
      - title: "Statistics"  # Overview topic
        sequence: 1
        prerequisites: []
        tags: ["overview", "start-here"]

      - title: "Statistical Inference"  # ENHANCED with Bouchaud Ch 1
        sequence: 2
        prerequisites: ["Statistics"]
        tags: ["foundational", "distributions", "heavy-tails"]
        enhanced_with: ["bouchaud_ch1"]  # NEW content marker

  # Path 2: Modeling & Prediction
  modeling_prediction:
    name: "Modeling & Prediction"
    description: "Regression and time series modeling"
    color: "#3b82f6"  # blue
    icon: "📈"
    sequence: 2
    topics:
      - title: "Regression Analysis"
        sequence: 1
        prerequisites: ["Statistical Inference"]
        tags: ["regression", "modeling"]

      - title: "Time Series Analysis"  # ENHANCED with Bouchaud Ch 4, Ch 10
        sequence: 2
        prerequisites: ["Regression Analysis", "Statistical Inference"]
        tags: ["time-series", "forecasting", "garch"]
        enhanced_with: ["bouchaud_ch4", "bouchaud_ch10"]  # Will be added

  # Path 3: Risk & Extreme Events (New topic from Bouchaud)
  risk_extreme_events:
    name: "Risk & Extreme Events"
    description: "Tail risk and extreme value theory"
    color: "#ef4444"  # red
    icon: "⚠️"
    sequence: 3
    topics:
      - title: "Extreme Value Theory"  # NEW topic from Bouchaud Ch 2
        sequence: 1
        prerequisites: ["Statistical Inference"]
        tags: ["extreme-events", "tail-risk", "advanced"]
        source: "bouchaud_ch2"
```

---

## What User Will See (After Configuration):

```
Statistics Category Sidebar:

📊 Statistical Inference & Distributions
  ├── ⭐ Statistics (overview)
  └── Statistical Inference (enhanced with Bouchaud Ch 1)
      └── New: Heavy-tailed distributions, Lévy, Student's t

📈 Modeling & Prediction
  ├── Regression Analysis
  └── Time Series Analysis (will be enhanced)
      └── Coming: Variograms, drawdown analysis

⚠️ Risk & Extreme Events
  └── Extreme Value Theory (new topic)
      └── Coming: Maximum of random variables, tail theory
```

---

## Comparison: Before vs After

### BEFORE (Current - Difficulty-Based):
```
Statistics
├── Difficulty 2
│   ├── Statistics
│   └── Statistical Inference
└── Difficulty 3
    ├── Regression Analysis
    └── Time Series Analysis
```
❌ No clear learning progression
❌ Arbitrary difficulty grouping
❌ Doesn't show what's been enhanced

### AFTER (Proposed - Learning Path-Based):
```
Statistics
├── 📊 Statistical Inference & Distributions (Start here)
│   ├── Statistics (overview)
│   └── Statistical Inference ⭐ Enhanced
│
├── 📈 Modeling & Prediction
│   ├── Regression Analysis
│   └── Time Series Analysis
│
└── ⚠️ Risk & Extreme Events
    └── Extreme Value Theory (New)
```
✅ Clear progression: Inference → Modeling → Risk
✅ Shows what's enhanced with Bouchaud content
✅ Optimal learning path

---

## Implementation Steps

### Step 1: Create Statistics Section in learning_paths.yaml

```yaml
# backend/config/learning_paths.yaml

# ... existing ML paths ...

# STATISTICS LEARNING PATHS
statistics_paths:
  foundational_inference:
    name: "Statistical Inference & Distributions"
    description: "⭐ Start here - Core statistical methods including heavy-tailed distributions"
    color: "#10b981"
    icon: "📊"
    topics:
      - title: "Statistics"
        sequence: 1
        prerequisites: []
        tags: ["overview", "start-here"]

      - title: "Statistical Inference"
        sequence: 2
        prerequisites: ["Statistics"]
        tags: ["foundational", "distributions", "heavy-tails", "levy", "students-t"]

  modeling_prediction:
    name: "Modeling & Prediction"
    description: "Regression and time series for forecasting"
    color: "#3b82f6"
    icon: "📈"
    topics:
      - title: "Regression Analysis"
        sequence: 1
        prerequisites: ["Statistical Inference"]
        tags: ["regression", "linear-models"]

      - title: "Time Series Analysis"
        sequence: 2
        prerequisites: ["Regression Analysis"]
        tags: ["time-series", "arma", "garch"]

  # Future: Add after creating new topic
  # risk_extreme_events:
  #   name: "Risk & Extreme Events"
  #   ...
```

### Step 2: Run Update Script

```bash
cd backend
python scripts/update_learning_paths.py --category statistics
```

### Step 3: Verify in Frontend

```bash
# Restart backend
# Refresh frontend
# Click Statistics → See new learning path groups!
```

---

## Timeline

**Immediate (Enhancement #1 - Done):**
- ✅ Enhanced inference.md with Bouchaud Ch 1
- Waiting: Apply learning paths to Statistics

**Next (Enhancement #2 & #3):**
- Enhance overview.md with Expected Shortfall (Bouchaud Ch 10)
- Enhance time_series.md with drawdown & variograms (Bouchaud Ch 4, 10)

**Future (Optional):**
- Create new topic: Extreme Value Theory (Bouchaud Ch 2)
- Add to risk_extreme_events learning path

---

## Decision Point

Before we proceed with indexing the enhanced inference.md, we should:

**Option A: Configure Learning Paths First** (Recommended)
1. Create learning_paths.yaml for Statistics
2. Apply learning path metadata to Statistics topics
3. THEN replace inference.md with enhanced version
4. Re-index everything together
5. User sees proper learning path organization

**Option B: Index Enhancement, Configure Paths Later**
1. Replace inference.md with enhanced version now
2. Re-index to vector store
3. Configure learning paths separately
4. User sees difficulty grouping temporarily, then learning paths

**Which approach do you prefer?**

