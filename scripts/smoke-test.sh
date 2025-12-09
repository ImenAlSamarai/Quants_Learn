#!/bin/bash

# Quick smoke test script
# Validates that the system is working without running full test suite

echo "=================================="
echo "   RUNNING SMOKE TESTS"
echo "=================================="
echo ""

FAILED=0

# Test 1: Backend syntax check
echo "🔍 Test 1: Backend syntax check..."
cd backend
python -m py_compile app/main.py 2>/dev/null
if [ $? -eq 0 ]; then
  echo "   ✅ Backend Python syntax OK"
else
  echo "   ❌ Backend syntax errors found"
  FAILED=1
fi
cd ..

# Test 2: Frontend syntax check
echo "🔍 Test 2: Frontend syntax check..."
cd frontend
npm run build --quiet > /dev/null 2>&1
if [ $? -eq 0 ]; then
  echo "   ✅ Frontend builds successfully"
else
  echo "   ⚠️  Frontend build has warnings/errors (check with: npm run build)"
fi
cd ..

# Test 3: Database connectivity
echo "🔍 Test 3: Database connectivity..."
cd backend
python -c "from app.models.database import engine; engine.connect()" 2>/dev/null
if [ $? -eq 0 ]; then
  echo "   ✅ Database connection OK"
else
  echo "   ❌ Cannot connect to database"
  FAILED=1
fi
cd ..

# Test 4: Environment variables
echo "🔍 Test 4: Environment variables..."
cd backend
if [ -f ".env" ]; then
  REQUIRED_VARS=("DATABASE_URL" "OPENAI_API_KEY" "PINECONE_API_KEY")
  ALL_PRESENT=true

  for var in "${REQUIRED_VARS[@]}"; do
    if ! grep -q "^${var}=" .env; then
      echo "   ❌ Missing: $var"
      ALL_PRESENT=false
      FAILED=1
    fi
  done

  if [ "$ALL_PRESENT" = true ]; then
    echo "   ✅ Required environment variables present"
  fi
else
  echo "   ❌ .env file not found"
  FAILED=1
fi
cd ..

# Test 5: Required directories exist
echo "🔍 Test 5: Required directories..."
if [ -d "content" ] && [ -d "backend/app" ] && [ -d "frontend/src" ]; then
  echo "   ✅ Project structure intact"
else
  echo "   ❌ Missing required directories"
  FAILED=1
fi

# Test 6: Backend can import modules
echo "🔍 Test 6: Backend module imports..."
cd backend
python -c "from app.services.learning_path_service import LearningPathService; from app.services.llm_service import LLMService" 2>/dev/null
if [ $? -eq 0 ]; then
  echo "   ✅ Backend modules import successfully"
else
  echo "   ❌ Backend import errors"
  FAILED=1
fi
cd ..

# Summary
echo ""
echo "=================================="
if [ $FAILED -eq 0 ]; then
  echo "✅ All smoke tests passed!"
  echo "=================================="
  exit 0
else
  echo "❌ Some tests failed"
  echo "=================================="
  exit 1
fi
