# Job-Based Personalization Refactoring Plan

**Branch:** `claude/job-based-personalization-01CixdohY7EHrx88bWG9bn7j`
**Date:** 2025-11-25
**Strategy:** Hard cut migration (clean slate for beta)

---

## Executive Summary

**Changes:**
- ❌ Remove: `learning_level` (1-5 difficulty system)
- ✅ Add: Job-based personalization (title, description, seniority, firm)
- ✅ Add: Auto-generated learning paths based on job requirements
- ✅ Add: Coverage checking (Tier 3: flag topics not in books)

**Impact:** 45 files affected (backend + frontend + scripts)

---

## Database Schema Changes

### User Model (`backend/app/models/database.py:121-176`)

**Remove:**
```python
learning_level = Column(Integer, default=3)  # DELETE THIS
```

**Add:**
```python
# Job-based personalization fields
job_title = Column(String(200))  # e.g., "Quantitative Researcher"
job_description = Column(Text)  # Full job posting text
job_seniority = Column(String(50))  # 'junior', 'mid', 'senior', 'not_specified'
firm = Column(String(200))  # e.g., "Citadel", "Two Sigma" (optional)
job_role_type = Column(String(100))  # 'quant_researcher', 'quant_trader', 'risk_quant', 'ml_engineer'
```

**Update:**
```python
@property
def profile_completion_percent(self):
    # Change from: name, email, education_level, learning_level
    # To: name, email, education_level, job_description
    total_fields = 4
    completed = 0
    if self.name: completed += 1
    if self.email: completed += 1
    if self.education_level: completed += 1
    if self.job_description and len(self.job_description) > 20: completed += 1
    # ... rest stays same
```

### GeneratedContent Model (`backend/app/models/database.py:195-213`)

**Change Cache Key Strategy:**

**Old:**
```python
difficulty_level = Column(Integer, nullable=False, index=True)  # 1-5
# Cache key: (node_id, content_type, difficulty_level)
```

**New:**
```python
job_profile_hash = Column(String(32), index=True)  # MD5 hash of job description
role_template_id = Column(String(50), index=True)  # For common roles: 'quant_researcher', 'quant_trader'
# Cache key: (node_id, content_type, role_template_id) OR (node_id, content_type, job_profile_hash)
```

### New Model: LearningPath

**Add new model:**
```python
class LearningPath(Base):
    """Auto-generated learning paths based on job requirements"""
    __tablename__ = 'learning_paths'

    id = Column(Integer, primary_key=True)
    user_id = Column(String(100), ForeignKey('users.user_id'), index=True)
    job_description = Column(Text)
    role_type = Column(String(100))  # Extracted role type

    # Path structure (JSON)
    stages = Column(JSON)  # [{"stage_name": "...", "topics": [...], "duration_weeks": 2}]

    # Coverage analysis
    covered_topics = Column(JSON)  # Topics available in our books
    uncovered_topics = Column(JSON)  # Topics not in books (external resources needed)
    coverage_percentage = Column(Integer)  # 0-100

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship('User', backref='learning_paths')
```

### Migration Impact

**Tables to modify:**
- ✅ `users` - Add job fields, remove learning_level
- ✅ `generated_content` - Change cache key strategy
- ✅ `learning_paths` - New table

**Data migration:**
- ❌ Delete all `generated_content` (hard cut)
- ⚠️ Users lose preferences (will re-set in new UI)

---

## Backend Service Changes

### 1. LLMService (`backend/app/services/llm_service.py`)

**Changes Required:**

**Add new methods:**
```python
def analyze_job_description(self, job_description: str) -> dict:
    """
    Use GPT-4o-mini to extract structured info from job posting
    Returns: {role_type, seniority, required_topics, implicit_topics, domain_focus, ...}
    """

def generate_explanation_for_job(
    self,
    topic: str,
    context_chunks: List[str],
    job_profile: dict,  # NEW: replaces difficulty int
    user_context: Optional[str] = None
) -> str:
    """Modified generate_explanation to use job context instead of difficulty"""
```

**Modify existing:**
```python
# KEEP for backward compatibility with scripts, but mark deprecated
def generate_explanation(
    self,
    topic: str,
    context_chunks: List[str],
    difficulty: int = 3,  # Keep for scripts
    user_context: Optional[str] = None
) -> str:
    # Wrapper that calls generate_explanation_for_job with default profile
```

**Strategy:**
- Keep `difficulty_profiles` dict for now (scripts use it)
- Add new job-based methods
- Migrate routes to use new methods
- Deprecate old methods in Phase 2

---

### 2. NEW: LearningPathService (`backend/app/services/learning_path_service.py`)

**Create new service:**

```python
class LearningPathService:
    """Generate and manage personalized learning paths based on job requirements"""

    def __init__(self):
        self.llm_service = llm_service
        self.vector_store = vector_store

    def generate_path_for_job(
        self,
        job_description: str,
        user_id: str,
        db: Session
    ) -> LearningPath:
        """
        1. Analyze job → extract topics (GPT-4o-mini)
        2. Check coverage for each topic (vector store)
        3. Sequence covered topics into learning stages (GPT-4o-mini)
        4. Return structured path + uncovered topics
        """

    def check_topic_coverage(
        self,
        topic: str,
        min_score: float = 0.75
    ) -> dict:
        """
        Tier 3: Check if topic is well-covered in books
        Returns: {covered: bool, source: str, confidence: float, external_resources: []}
        """

    def get_next_topic(
        self,
        user_id: str,
        db: Session
    ) -> Optional[Node]:
        """Based on user's learning path and completed topics"""

    def sequence_topics(
        self,
        topics: List[str],
        job_profile: dict,
        db: Session
    ) -> List[dict]:
        """
        Use LLM to create optimal learning sequence
        Considers: prerequisites, job relevance, pedagogical flow
        """
```

**Key Logic:**

```python
def check_topic_coverage(self, topic: str, min_score: float = 0.75) -> dict:
    # Search vector store
    matches = vector_store.search(query=topic, top_k=10)

    if not matches or matches[0]['score'] < min_score:
        # NOT COVERED - provide external resources
        return {
            "covered": False,
            "topic": topic,
            "confidence": matches[0]['score'] if matches else 0,
            "external_resources": self._get_external_resources(topic)
        }

    # COVERED - extract source book
    return {
        "covered": True,
        "topic": topic,
        "confidence": matches[0]['score'],
        "source": matches[0]['metadata'].get('source'),  # ESL/DL/Bouchaud
        "num_chunks": len([m for m in matches if m['score'] > min_score])
    }
```

---

### 3. Content Routes (`backend/app/routes/content.py`)

**Changes Required:**

**Line 18-26: get_or_create_user()**
```python
# OLD:
user = User(user_id=user_id, learning_level=3)

# NEW:
user = User(user_id=user_id)  # No default learning_level
```

**Line 48-50: Get user profile**
```python
# OLD:
user = get_or_create_user(request.user_id, db)
difficulty_level = user.learning_level

# NEW:
user = get_or_create_user(request.user_id, db)
job_profile = None
cache_key = None

if user.job_description:
    # Parse job if not already cached
    job_profile = llm_service.analyze_job_description(user.job_description)

    # Determine cache strategy
    if user.job_role_type in COMMON_ROLE_TEMPLATES:
        cache_key = user.job_role_type  # Use template for cache
    else:
        cache_key = hashlib.md5(user.job_description.encode()).hexdigest()[:16]
else:
    # Fallback: user hasn't set job preferences
    cache_key = "default"
    job_profile = {"role_type": "general", "seniority": "mid"}
```

**Line 59-65: Cache lookup**
```python
# OLD:
cached = db.query(GeneratedContent).filter(
    GeneratedContent.node_id == request.node_id,
    GeneratedContent.content_type == request.query_type,
    GeneratedContent.difficulty_level == difficulty_level,
    ...
).first()

# NEW:
cached = db.query(GeneratedContent).filter(
    GeneratedContent.node_id == request.node_id,
    GeneratedContent.content_type == request.query_type,
    GeneratedContent.role_template_id == cache_key,  # OR job_profile_hash
    ...
).first()
```

**Line 106-111: Generate explanation**
```python
# OLD:
generated_content = llm_service.generate_explanation(
    topic=node.title,
    context_chunks=context_chunks,
    difficulty=difficulty_level,
    user_context=request.user_context
)

# NEW:
generated_content = llm_service.generate_explanation_for_job(
    topic=node.title,
    context_chunks=context_chunks,
    job_profile=job_profile,
    user_context=request.user_context
)
```

**Line 176-187: Save to cache**
```python
# OLD:
cached_content = GeneratedContent(
    node_id=request.node_id,
    content_type=request.query_type,
    difficulty_level=difficulty_level,
    ...
)

# NEW:
cached_content = GeneratedContent(
    node_id=request.node_id,
    content_type=request.query_type,
    role_template_id=cache_key if user.job_role_type in COMMON_ROLE_TEMPLATES else None,
    job_profile_hash=cache_key if user.job_role_type not in COMMON_ROLE_TEMPLATES else None,
    ...
)
```

---

### 4. User Routes (`backend/app/routes/users.py`)

**Add new endpoints:**

```python
@router.patch("/{user_id}/job-profile")
async def update_job_profile(
    user_id: str,
    job_data: JobProfileUpdate,
    db: Session = Depends(get_db)
):
    """Update user's job target and generate learning path"""

    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404)

    # Update job fields
    user.job_title = job_data.job_title
    user.job_description = job_data.job_description
    user.job_seniority = job_data.job_seniority
    user.firm = job_data.firm

    # Analyze job and extract role type
    job_profile = llm_service.analyze_job_description(job_data.job_description)
    user.job_role_type = job_profile.get('role_type', 'not_specified')

    db.commit()

    # Generate learning path
    learning_path_service = LearningPathService()
    path = learning_path_service.generate_path_for_job(
        job_description=job_data.job_description,
        user_id=user_id,
        db=db
    )

    return {
        "user": user,
        "learning_path": path,
        "coverage_percentage": path.coverage_percentage
    }
```

---

### 5. Progress Service (`backend/app/services/progress_service.py`)

**No major changes** - already works with user progress independent of difficulty level.

---

## Frontend Changes

### 1. UserSettings Component (`frontend/src/components/UserSettings.jsx`)

**Replace difficulty level selector with job input:**

**Remove:**
```jsx
// Lines 14-50: levels array with 5 difficulty options
// Lines 156-187: Level selection UI
```

**Add:**
```jsx
const [jobTitle, setJobTitle] = useState('');
const [jobDescription, setJobDescription] = useState('');
const [jobSeniority, setJobSeniority] = useState('not_specified');
const [firm, setFirm] = useState('');
const [useTemplate, setUseTemplate] = useState(true);
const [selectedTemplate, setSelectedTemplate] = useState('');

const commonRoles = [
  { id: 'quant_researcher', name: 'Quantitative Researcher', description: 'Research-focused, PhD level' },
  { id: 'quant_trader', name: 'Quantitative Trader (HFT)', description: 'Fast execution, market making' },
  { id: 'risk_quant', name: 'Risk Analyst', description: 'Risk modeling, VaR, stress testing' },
  { id: 'ml_engineer', name: 'ML Engineer (Finance)', description: 'Production ML systems' },
];

// UI: Toggle between template selection and custom job paste
```

---

### 2. NEW: LearningPathView Component (`frontend/src/components/LearningPathView.jsx`)

**Create new component:**

```jsx
const LearningPathView = ({ userId }) => {
  const [learningPath, setLearningPath] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchLearningPath();
  }, [userId]);

  const fetchLearningPath = async () => {
    const response = await fetch(`/api/users/${userId}/learning-path`);
    const data = await response.json();
    setLearningPath(data);
    setLoading(false);
  };

  return (
    <div className="learning-path-container">
      <JobTargetHeader
        job={learningPath.job_title}
        coverage={learningPath.coverage_percentage}
      />

      <PathStages stages={learningPath.stages} />

      <UncoveredTopics topics={learningPath.uncovered_topics} />

      <NextSteps currentStage={...} />
    </div>
  );
};
```

---

## Migration Scripts

### 1. Database Migration (`backend/management/commands/migrate_to_job_based.py`)

**Create new command:**

```python
def migrate_database():
    """Migrate from difficulty-based to job-based system"""

    print("🔄 Starting migration to job-based personalization...\n")

    # Step 1: Add new columns to users table
    print("Step 1: Adding job fields to users table...")
    execute_sql("""
        ALTER TABLE users
        ADD COLUMN job_title VARCHAR(200),
        ADD COLUMN job_description TEXT,
        ADD COLUMN job_seniority VARCHAR(50),
        ADD COLUMN firm VARCHAR(200),
        ADD COLUMN job_role_type VARCHAR(100);
    """)

    # Step 2: Modify generated_content table
    print("Step 2: Updating generated_content cache strategy...")
    execute_sql("""
        ALTER TABLE generated_content
        ADD COLUMN role_template_id VARCHAR(50),
        ADD COLUMN job_profile_hash VARCHAR(32);

        CREATE INDEX idx_role_template ON generated_content(role_template_id);
        CREATE INDEX idx_job_hash ON generated_content(job_profile_hash);
    """)

    # Step 3: Create learning_paths table
    print("Step 3: Creating learning_paths table...")
    execute_sql("""
        CREATE TABLE learning_paths (
            id SERIAL PRIMARY KEY,
            user_id VARCHAR(100) REFERENCES users(user_id),
            job_description TEXT,
            role_type VARCHAR(100),
            stages JSON,
            covered_topics JSON,
            uncovered_topics JSON,
            coverage_percentage INTEGER,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );

        CREATE INDEX idx_learning_path_user ON learning_paths(user_id);
    """)

    # Step 4: HARD CUT - Delete old cached content
    print("Step 4: Clearing old cached content (hard cut)...")
    deleted = db.query(GeneratedContent).delete()
    print(f"  ✓ Deleted {deleted} cached explanations")

    # Step 5: Keep learning_level column for backward compat with scripts
    print("Step 5: Keeping learning_level for script compatibility...")
    print("  ⚠️  Will be removed in Phase 2")

    print("\n✅ Migration complete!")
    print("Users will need to set job preferences in new UI")
```

---

## Implementation Order (Step-by-Step)

### Phase 1: Database & Core Services (Backend)
1. ✅ Create migration script
2. ✅ Add new columns to User model
3. ✅ Create LearningPath model
4. ✅ Update GeneratedContent model (cache keys)
5. ✅ Create LearningPathService
6. ✅ Update LLMService (add job-based methods)
7. ✅ Run migration on dev database

### Phase 2: Routes (Backend)
8. ✅ Update content.py (use job profile instead of difficulty)
9. ✅ Update users.py (add job profile endpoints)
10. ✅ Add learning path generation endpoint
11. ✅ Test API endpoints manually

### Phase 3: Frontend
12. ✅ Update UserSettings.jsx (job input UI)
13. ✅ Create LearningPathView.jsx
14. ✅ Update App.jsx routing
15. ✅ Add learning path styles

### Phase 4: Testing
16. ✅ End-to-end test: Set job → Generate path → Request content
17. ✅ Verify cache working correctly
18. ✅ Test coverage checking (Tier 3)

---

## Files to Modify (Summary)

### Critical (Must Change)
- ✅ `backend/app/models/database.py` - Schema changes
- ✅ `backend/app/services/llm_service.py` - Job-based methods
- ✅ `backend/app/routes/content.py` - Cache & generation logic
- ✅ `backend/app/routes/users.py` - Job profile endpoints
- ✅ `frontend/src/components/UserSettings.jsx` - Job input UI
- ✅ **NEW:** `backend/app/services/learning_path_service.py`
- ✅ **NEW:** `backend/management/commands/migrate_to_job_based.py`
- ✅ **NEW:** `frontend/src/components/LearningPathView.jsx`

### Optional (Scripts - can keep using difficulty for now)
- ⚠️ `backend/scripts/*` - Many scripts use difficulty, keep for now
- ⚠️ Can migrate scripts in Phase 2

### Documentation
- ✅ Update `README.md`
- ✅ Update `ARCHITECTURE.md`
- ✅ Update `PHASE_2_PLAN.md`

---

## Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Cache invalidation loses all content | Medium | Expected (hard cut), regenerates on demand |
| LLM parsing job descriptions fails | High | Fallback to "general" template, log errors |
| Beta users confused by new UI | Medium | Add onboarding flow, clear instructions |
| Coverage checking false negatives | Medium | Tune threshold (0.75), manual review for beta |
| API costs spike from regeneration | Low | Lazy generation + template caching |

---

## Success Criteria

**Backend:**
- ✅ Migration runs without errors
- ✅ Job profile extracted correctly from descriptions
- ✅ Learning paths generated with proper sequencing
- ✅ Coverage checking accurately identifies gaps
- ✅ Cache works with new key strategy

**Frontend:**
- ✅ Users can input job (template or custom)
- ✅ Learning path displays clearly
- ✅ Uncovered topics shown with external resources
- ✅ Settings save correctly

**Integration:**
- ✅ Content explanations tailored to job role
- ✅ Cache hit rate >50% for template roles
- ✅ No errors in console

**Beta Test:**
- ✅ 5 users successfully set job profiles
- ✅ Learning paths make sense for their roles
- ✅ Content quality meets expectations
- ✅ Users understand what's covered vs. external

---

## Next Steps

**Ready to proceed with implementation?**
- Branch created ✓
- Impact analyzed ✓
- Refactoring plan documented ✓

**Awaiting confirmation to begin Phase 1: Database & Core Services**
