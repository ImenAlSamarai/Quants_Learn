# Deprecated Files - DO NOT USE

**Last Updated:** 2025-12-09

This document lists files that are kept for backward compatibility but should **NOT** be used for new features or modifications.

---

## ⚠️ Important: Check This Before Coding

**Before editing or exploring files, check:**
1. Is the file listed below as deprecated?
2. Does the file have a "DEPRECATED" comment at the top?
3. What is the recommended replacement?

**When in doubt:** Ask which file to edit before implementing features.

---

## Frontend - Old Explore Page System

**Deprecated Date:** 2025-11-28 (Phase 3 - Job-based personalization)
**Reason:** Moved from explore-based navigation to job-based personalized learning paths
**Phase to Remove:** Refactoring Phase 5

| File Path | Status | Replacement | Notes |
|-----------|--------|-------------|-------|
| `frontend/src/pages/LandingPage.jsx` | 🔴 DEPRECATED | `frontend/src/pages/Home.jsx` | Old `/explore` route - Use Home.jsx for main entry point (route: `/`) |
| `frontend/src/styles/old-design.css` | ⚠️ CHECK | `frontend/src/styles/Home.css` | May contain old styling - verify before use |

### Route Mapping

| Old Route | Status | New Route | Component |
|-----------|--------|-----------|-----------|
| `/explore` | 🔴 Deprecated | `/` | `Home.jsx` - Main job creation form |
| `/` (old home) | 🔴 Changed | `/` | Now uses job-based system |

---

## Backend - Difficulty-Based System

**Deprecated Date:** 2025-11-28 (Phase 2 - Backend job-based personalization)
**Reason:** Moved from 5-level difficulty system to job description analysis
**Phase to Remove:** Refactoring Phase 4 (Database cleanup)

| File/Field | Status | Replacement | Notes |
|------------|--------|-------------|-------|
| `backend/app/models/database.py:learning_level` | 🟡 DEPRECATED | `job_description` field | Old 1-5 difficulty level - keep for backward compat |
| Difficulty-based prompts | 🔴 DEPRECATED | Job-based topic extraction | See `learning_path_service.py` |

### Database Fields

| Field Name | Status | Replacement | Migration Status |
|------------|--------|-------------|------------------|
| `User.learning_level` | 🟡 Deprecated | `User.job_description` | Data not migrated - both exist |
| `Node.difficulty_level` | ✅ Active | Keep - still useful for sorting | N/A |

---

## Content - Old Structure

**Status:** ⚠️ Under review

| Directory | Status | Notes |
|-----------|--------|-------|
| `content/old_tutorials/` | ❓ Unknown | Check if exists - may need cleanup |

---

## How to Handle Deprecated Files

### For Developers

**Do NOT:**
- ❌ Use deprecated files for new features
- ❌ Extend deprecated functionality
- ❌ Copy code from deprecated files

**Do:**
- ✅ Use replacement files listed above
- ✅ Add deprecation comments if you find unmarked files
- ✅ Update this document when you identify deprecated code
- ✅ Ask user to confirm correct file before implementing

### For Claude (AI Assistant)

**Before implementing any feature:**

1. **Check this file first** - Is the target file deprecated?
2. **Read file header** - Look for "DEPRECATED" comments
3. **Confirm with user:** "I'll edit [file]. This is the correct active file, right?"
4. **If deprecated found:** "I found [file] but it's deprecated. Should I use [replacement] instead?"

### For Refactoring

**Phase 4 (Database Layer):**
- Remove `learning_level` field after data migration
- Clean up difficulty-based logic

**Phase 5 (Service Decomposition):**
- Move `LandingPage.jsx` to `frontend/src/pages/_deprecated/`
- Or delete entirely after confirming no usage
- Remove old CSS files

---

## Deprecation Status Legend

| Symbol | Meaning | Action |
|--------|---------|--------|
| 🔴 DEPRECATED | Do not use | Use replacement immediately |
| 🟡 DEPRECATED | Kept for backward compat | Use replacement for new code |
| ⚠️ CHECK | Uncertain status | Verify before use |
| ❓ UNKNOWN | Needs investigation | Ask user or investigate |
| ✅ ACTIVE | Currently in use | Safe to use |

---

## Recently Deprecated (Last 30 Days)

- **2025-12-09:** Identified `LandingPage.jsx` as deprecated during Hello World workflow test
- **2025-11-28:** Phase 3 completion - Job-based personalization replaced explore system

---

## How to Report Deprecated Files

If you find code that should be deprecated:

1. Add "DEPRECATED" comment to file header
2. Update this document with entry
3. Commit: `git commit -m "Mark [file] as deprecated"`
4. Update CURRENT_STATE.md

---

## Questions?

- Check `.claude/README.md` for workflow guidance
- Check `CURRENT_STATE.md` for current project status
- Ask user to confirm correct file before implementing

---

**Remember:** When in doubt, ask which file to use. Better to clarify than implement in wrong location!
