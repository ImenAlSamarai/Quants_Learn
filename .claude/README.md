# Claude Code Configuration

This project is configured with Claude Code support for intelligent development assistance.

## Enabled Plugins

**Core Development Plugins:**
- `system@local` - Project audit, cleanup, setup, and status commands
- `workflow@local` - Explore, plan, next, ship workflow commands
- `memory@local` - Session handoff and memory management
- `development@local` - Code analysis, review, testing, fixes, and git operations
- `transition@local` - Smooth transitions between development sessions

## Available Commands

Run `/help` in Claude Code to see all available commands. Key workflows:

### Project Analysis
- `/development:analyze` - Understand project structure and architecture
- `/workflow:explore` - Systematic exploration of requirements and codebase

### Development Workflow
- `/workflow:plan` - Create detailed implementation plans
- `/workflow:next` - Execute next task from implementation plan
- `/workflow:ship` - Deliver completed work with validation

### Code Quality
- `/development:review` - Code review for bugs, design flaws, and quality issues
- `/development:test` - Test-driven development workflow
- `/development:fix` - Debug errors and apply fixes

### Git Operations
- `/development:git commit` - Create commits
- `/development:git pr` - Manage pull requests
- `/development:git issue` - Work with GitHub issues

## MCP Servers

**Serena** - Semantic code understanding
- Provides intelligent code analysis and symbol search
- Reduces token usage by 70-90% for large codebases
- Available tools: `find_symbol`, `search_for_pattern`, `get_symbols_overview`, `find_referencing_symbols`

## Project Structure

This is a **Quantitative Finance Learning Platform** with:
- **Backend**: Python/Django with OpenAI integration, PostgreSQL, Pinecone
- **Frontend**: React + Vite + Tailwind CSS
- **Content**: Educational markdown content on quant finance topics

## Permissions

Standard permissions are configured to allow:
- Python/Node.js development commands (pytest, npm, git)
- Reading source files (*.py, *.js, *.md, etc.)
- Writing/editing project files in backend, frontend, content, and tests directories
- Serena MCP server operations

Denied operations:
- Destructive commands (rm -rf, sudo)
- Modifying .env files (security)

## ⚠️ MANDATORY: Feature Branch Workflow

**Before implementing ANY feature, Claude MUST:**

1. **Check current branch:** `git branch`
2. **Create feature branch:** `git checkout -b feature/[descriptive-name]`
3. **Verify new branch:** `git branch` (check for * on feature branch)
4. **Check for deprecated files:** Read `DEPRECATED_FILES.md`
5. **Confirm file location with user:** "I'll edit [file]. Is this the correct active file?"
6. **Then proceed with implementation**

**NEVER work directly on develop or main branch!**

**Branch naming:** `feature/[short-description]` (lowercase, hyphens)
- Examples: `feature/quiz-generation`, `feature/hello-world-test`

## ⚠️ CRITICAL: Check for Deprecated Files

**Before exploring or editing any file:**

1. **Read DEPRECATED_FILES.md** - Lists all deprecated components
2. **Check file header** - Look for "DEPRECATED - DO NOT USE" comments
3. **Confirm with user** - Ask which file to use if uncertain

**Current Active Files:**
- ✅ Main page: `frontend/src/pages/Home.jsx` (route: `/`)
- ❌ DEPRECATED: `frontend/src/pages/LandingPage.jsx` (old explore page)

**When implementing features:**
- Ask user: "Which page/component should show this feature?"
- Ask user: "Is this route `/` (Home) or another page?"
- Confirm: "I'll edit [file]. This is correct, right?"

**If you find a deprecated file:**
- STOP - Do not implement in deprecated files
- Check DEPRECATED_FILES.md for replacement
- Ask user to confirm correct location

**After feature complete:**
1. Test: `./scripts/smoke-test.sh`
2. Merge to develop: `git checkout develop && git merge feature/[name]`
3. Delete feature branch: `git branch -d feature/[name]`
4. Update `CURRENT_STATE.md`

## Next Steps

1. Run `/workflow:explore` to understand the current project state
2. Use `/development:analyze` for architectural insights
3. Create implementation plans with `/workflow:plan`
4. Review code quality with `/development:review`

For more information, visit the [Claude Code documentation](https://docs.anthropic.com/claude-code).
