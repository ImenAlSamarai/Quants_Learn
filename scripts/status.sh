#!/bin/bash

# Quick status check script
# Shows current branch, last commit, database status, and current state

echo "=================================="
echo "   QUANTS_LEARN STATUS CHECK"
echo "=================================="
echo ""

# Check current branch
echo "📍 Current Branch:"
git branch --show-current
echo ""

# Check last commit
echo "📝 Last Commit:"
git log -1 --oneline
echo ""

# Check for uncommitted changes
echo "🔍 Uncommitted Changes:"
if [ -z "$(git status --porcelain)" ]; then
  echo "   ✅ Working directory clean"
else
  echo "   ⚠️  You have uncommitted changes:"
  git status --short
fi
echo ""

# Check database status
echo "💾 Database Status:"
cd backend && python setup.py --status 2>/dev/null || echo "   ❌ Unable to check database (is backend set up?)"
cd ..
echo ""

# Show current state summary
echo "📊 Current State (from CURRENT_STATE.md):"
if [ -f "CURRENT_STATE.md" ]; then
  echo "   Last Updated: $(grep "Last Updated:" CURRENT_STATE.md | cut -d' ' -f3-)"
  echo "   Branch: $(grep "Branch:" CURRENT_STATE.md | head -1 | cut -d'`' -f2)"
  echo ""
  echo "   Quick Status:"
  grep -A 10 "## 📊 Quick Status" CURRENT_STATE.md | grep "^|" | head -8
else
  echo "   ⚠️  CURRENT_STATE.md not found"
fi
echo ""

echo "=================================="
echo "💡 Next: Read CURRENT_STATE.md for details"
echo "=================================="
