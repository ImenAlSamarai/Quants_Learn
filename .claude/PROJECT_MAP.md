# Project Map: Quants_Learn

*Generated: 2025-12-09*
*Last Updated: 2025-12-09*

## Quick Overview
- **Type**: Full-stack web application
- **Primary Language**: Python (Backend), JavaScript (Frontend)
- **Frameworks**: FastAPI, React, Vite, PostgreSQL, Pinecone
- **Location**: /Users/imenalsamarai/Documents/projects_MCP/Quants_Learn

## Project Purpose
Job-based quantitative finance learning platform with personalized learning paths generated from job descriptions.

## Current Branch
- **Main Development Branch**: `dev`
- **NOT "develop"** - Documentation refers to "develop" but actual branch name is different

## Directory Structure

### Backend (Python/FastAPI)
- `backend/app/` - Main application code (FastAPI)
  - `backend/app/routes/` - API endpoints
  - `backend/app/services/` - Business logic (LLM, learning paths, content generation)
  - `backend/app/models/` - Database models (SQLAlchemy)
- `backend/scripts/` - Utility scripts (59 scripts for various tasks)
- `backend/tests/` - Tests (to be implemented)

### Frontend (React/Vite)
- `frontend/src/pages/` - Page components
  - **ACTIVE**: `Home.jsx` - Main entry page (route: `/`)
  - **DEPRECATED**: `LandingPage.jsx` - Old explore page (route: `/explore`)
- `frontend/src/components/` - Reusable components
- `frontend/src/services/` - API client
- `frontend/src/styles/` - CSS styling

### Content
- `content/` - Educational markdown content
  - `content/statistics/` - Statistics topics
  - `content/finance/` - Finance topics
  - etc.

### Documentation
- `CURRENT_STATE.md` - **PRIMARY STATUS DOCUMENT** (always read this first)
- `DEPRECATED_FILES.md` - Lists deprecated code (check before implementing)
- `DEVELOPMENT_WORKFLOW.md` - Git workflow and development process
- `.claude/README.md` - Claude Code configuration and workflow

## Key Files

### Entry Points
- `backend/app/main.py` - FastAPI application entry point
- `frontend/src/main.jsx` - React application entry point

### Critical Service Files
- `backend/app/services/learning_path_service.py` - Job analysis and path generation (501 lines)
- `backend/app/services/llm_service.py` - OpenAI content generation (470 lines)
- `backend/app/routes/content.py` - Content API endpoints (412 lines)

### Configuration
- `backend/.env` - Environment variables (API keys, DB credentials)
- `backend/requirements.txt` - Python dependencies
- `frontend/package.json` - Node.js dependencies

## Patterns & Conventions

### Architecture
- **Backend**: FastAPI with SQLAlchemy ORM
- **Frontend**: React with Zustand for state management
- **Database**: PostgreSQL for structured data
- **Vector Store**: Pinecone for content embeddings
- **LLM**: OpenAI GPT-4o-mini (with quality issues on topic extraction)

### Known Issues
- **CRITICAL**: Topic extraction uses GPT-4o-mini, produces vague topics instead of specific ones
- Debug code still in production (console.log, print statements)
- No automated tests
- Configuration scattered across files

### Git Workflow
- **Main Branch**: `dev` (NOT "develop")
- **Feature Branches**: `feature/[name]` created from main development branch
- **Merge Strategy**: Merge feature branches back to main development branch when complete

### Development Commands
- Backend: `cd backend && source venv/bin/activate && python -m app.main`
- Frontend: `cd frontend && npm run dev`
- Health Check: `cd backend && python setup.py --status`

## Current State (as of 2025-12-09)

### What's Working ✅
- Backend API running on port 8000
- Frontend dev server on port 5173
- Job-based learning path generation
- Content generation with LLM
- Mind map visualization
- Progress tracking

### What's Broken ⚠️
- Topic extraction quality (too generic, not specific enough)

### Recent Work
- ✅ Workflow test completed (Hello World feature)
- ✅ Deprecation documentation system added
- ✅ Fixed confusion between old (LandingPage.jsx) and new (Home.jsx) code

### Next Priorities
1. Fix topic extraction quality (upgrade to GPT-4o)
2. Code hygiene cleanup (remove debug code)
3. Add more content

## Deprecation System

### Check Before Implementing
1. Read `DEPRECATED_FILES.md` first
2. Look for "DEPRECATED" comments in file headers
3. Confirm correct file with user

### Known Deprecated Files
- `frontend/src/pages/LandingPage.jsx` - Use `Home.jsx` instead
- Old difficulty-based system - Now uses job descriptions

## Documentation Files Priority

**Always read in this order:**
1. `CURRENT_STATE.md` - Current project status
2. `DEPRECATED_FILES.md` - What NOT to use
3. `.claude/README.md` - Workflow instructions
4. `DEVELOPMENT_WORKFLOW.md` - Detailed git workflow

## Phase Completion
- ✅ Phase 1: Difficulty-based content (deprecated)
- ✅ Phase 2: Backend job-based personalization
- ✅ Phase 3: Frontend job-based UI
- 🚧 Phase 4: Quality improvements (in progress)
