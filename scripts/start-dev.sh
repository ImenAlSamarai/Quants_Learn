#!/bin/bash

# Development environment startup script
# Starts backend and frontend servers in separate processes

echo "=================================="
echo "  STARTING DEVELOPMENT ENVIRONMENT"
echo "=================================="
echo ""

# Check if already on correct branch
CURRENT_BRANCH=$(git branch --show-current)
EXPECTED_BRANCH="dev"

if [ "$CURRENT_BRANCH" != "$EXPECTED_BRANCH" ]; then
  echo "⚠️  Warning: You're on branch '$CURRENT_BRANCH'"
  echo "   Expected: '$EXPECTED_BRANCH'"
  echo ""
  read -p "Switch to correct branch? (y/n) " -n 1 -r
  echo
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    git checkout "$EXPECTED_BRANCH"
  fi
fi

# Check database status
echo "📋 Checking database status..."
cd backend
python setup.py --status
if [ $? -ne 0 ]; then
  echo ""
  echo "❌ Database check failed. Please run setup first:"
  echo "   cd backend && python setup.py"
  exit 1
fi
cd ..

echo ""
echo "✅ Database ready"
echo ""
echo "🚀 Starting servers..."
echo ""
echo "   Backend will be at: http://localhost:8000"
echo "   Frontend will be at: http://localhost:5173"
echo "   API docs at: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""
echo "=================================="
echo ""

# Function to cleanup background processes
cleanup() {
  echo ""
  echo "Stopping servers..."
  kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
  exit 0
}

trap cleanup INT TERM

# Start backend
cd backend
source venv/bin/activate
python -m app.main &
BACKEND_PID=$!
cd ..

# Wait a bit for backend to start
sleep 3

# Start frontend
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

# Wait for both processes
wait
