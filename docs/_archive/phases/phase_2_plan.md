# Phase 2: Professional Progress Tracking

## Objective
Build professional progress tracking system for PhD candidates preparing for quant finance interviews, with recruiter pipeline features.

## Design Principles
- **Professional aesthetic**: Bloomberg Terminal meets Coursera
- **No gamification**: No confetti, badges, or game mechanics
- **Clear progress**: Sober but clear progress indicators
- **Recruiter-ready**: Store candidate data for future talent pipeline

---

## Implementation Steps

### **Step 1: Database Schema Extensions** ✅
**Goal:** Add fields to track candidate profiles and progress

**1.1 User Model Extensions**
- Add `full_name`, `email`, `phone` (candidate contact)
- Add `cv_url`, `linkedin_url` (recruiter pipeline)
- Add `education_level` (undergraduate, masters, phd)
- Add `current_role`, `years_experience`
- Add `target_roles` (array: quant researcher, trader, etc.)
- Add `profile_completion_percent` (calculated field)
- Add `interview_readiness_score` (0-100)
- Add `created_at`, `last_active_at`

**1.2 Progress Tracking Tables**
- `competencies` table (skill mastery tracking)
  - user_id, category, level, topics_completed, topics_total
- `study_sessions` table (time tracking)
  - user_id, node_id, duration_seconds, completed_at

**1.3 Migration Plan**
- Create migration script (backward compatible)
- Add database upgrade command to manage.py
- Test on development database first

**Files to modify:**
- `backend/app/models/database.py`
- `backend/management/commands/migrate_db.py` (new)

---

### **Step 2: Progress Calculation Logic** ✅
**Goal:** Calculate profile completion % and interview readiness score

**2.1 Profile Completion Calculator**
- Required fields: name, email, education_level, learning_level (25% each)
- Optional fields: cv_url, linkedin_url, current_role, target_roles (bonus)
- Return 0-100%

**2.2 Interview Readiness Calculator**
- Category coverage: % of categories with progress (40%)
- Topic completion: Average % across categories (40%)
- Study consistency: Active last 7 days bonus (20%)
- Return 0-100 score

**2.3 Competency Tracker**
- Per category: beginner (1-33%), intermediate (34-66%), advanced (67-100%)
- Based on topics completed at current learning level

**Files to create:**
- `backend/app/services/progress_service.py`

---

### **Step 3: Backend API Endpoints** ✅
**Goal:** Expose progress data to frontend

**3.1 Profile Management**
- `PATCH /api/users/{user_id}/profile` - Update profile fields
- `GET /api/users/{user_id}/profile` - Get full profile with completion %

**3.2 Progress Dashboard**
- `GET /api/users/{user_id}/dashboard` - All dashboard data
  - Profile completion %
  - Interview readiness score
  - Competencies breakdown
  - Recent activity
  - Recommended next topics

**3.3 Study Session Tracking**
- `POST /api/progress/session` - Log study session
  - node_id, duration_seconds

**Files to modify:**
- `backend/app/routes/users.py`
- `backend/app/routes/progress.py`

---

### **Step 4: Frontend Components** ✅
**Goal:** Professional progress UI matching design principles

**4.1 Profile Setup Modal** (First-time users)
- Clean, professional form
- Fields: name, email, education level, current role
- Optional: CV upload, LinkedIn, target roles
- Shows completion % as you fill

**4.2 Progress Dashboard** (Landing page replacement)
- **Top Section**: Profile summary card
  - Name, role, education
  - Profile completion % (progress bar)
  - Interview readiness score (circular gauge)

- **Middle Section**: Competencies grid
  - 4 cards (Statistics, Probability, Linear Algebra, Calculus)
  - Each shows: progress bar, level (beginner/intermediate/advanced)
  - Color: professional blues/grays (no bright colors)

- **Bottom Section**: Activity & Recommendations
  - Last studied topics
  - Recommended next topics
  - Study streak (days active)

**4.3 Profile Settings** (Enhanced existing UserSettings)
- Add profile fields to settings modal
- Show profile completion %
- CV upload field (future: actual upload, now: URL)

**Files to create:**
- `frontend/src/components/dashboard/ProfileSetup.jsx`
- `frontend/src/components/dashboard/ProgressDashboard.jsx`
- `frontend/src/components/dashboard/CompetencyCard.jsx`
- `frontend/src/components/dashboard/ProfileSummary.jsx`

**Files to modify:**
- `frontend/src/components/UserSettings.jsx`
- `frontend/src/App.jsx` (routing)
- `frontend/src/styles/dashboard.css` (new)

---

### **Step 5: Integration & Testing** ✅
**Goal:** Ensure seamless frontend-backend integration

**5.1 Test Plan**
- [ ] Database migration runs successfully
- [ ] Profile completion calculation works (0%, 25%, 50%, 75%, 100%)
- [ ] Interview readiness calculation works
- [ ] Competencies update when topics completed
- [ ] Frontend displays correct progress data
- [ ] Profile setup flow works for new users
- [ ] Dashboard loads without errors
- [ ] Settings modal saves profile fields

**5.2 Manual Testing**
- New user flow: profile setup → dashboard → complete topic → verify progress updates
- Existing user flow: dashboard loads → settings update → verify changes
- Edge cases: incomplete profile, no progress, all topics completed

**5.3 Verification**
- Run health check
- Check database constraints
- Test API endpoints with curl
- Verify frontend console has no errors

---

## Success Criteria

**Backend:**
- ✅ Database schema supports all profile fields
- ✅ Progress calculations return correct values
- ✅ API endpoints respond with proper data
- ✅ No breaking changes to existing functionality

**Frontend:**
- ✅ Professional aesthetic (Bloomberg-inspired)
- ✅ Progress indicators clear and accurate
- ✅ No gamification elements
- ✅ Mobile responsive
- ✅ Integrates seamlessly with existing Study/Explore modes

**Testing:**
- ✅ All API endpoints tested
- ✅ Profile completion % accurate
- ✅ Interview readiness score makes sense
- ✅ No console errors
- ✅ Database migrations work

---

## Timeline

- **Step 1 (Database):** ~2 hours
- **Step 2 (Progress Logic):** ~1 hour
- **Step 3 (API Endpoints):** ~1 hour
- **Step 4 (Frontend):** ~3 hours
- **Step 5 (Testing):** ~1 hour

**Total:** ~8 hours of development work

---

## Notes

- Keep it simple: Don't over-engineer
- Professional > Flashy: Subtle, clean design
- Recruiter-ready: All data structured for future dashboard
- Backward compatible: Existing users shouldn't break
