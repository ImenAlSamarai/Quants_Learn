#!/bin/bash

# Script to pull latest changes for Quant Learning Platform
# Run this from your local machine

echo "🔄 Pulling latest changes from GitHub..."
echo ""

# Navigate to project root
cd "$(dirname "$0")"

# Pull latest changes
git pull origin claude/debug-work-status-01HeAn48N3zJvNZGNNtJgpda

echo ""
echo "✅ Changes pulled successfully!"
echo ""
echo "📝 To verify the fix, check that frontend/src/styles/index.css starts with:"
echo "   @import 'tailwindcss';"
echo "   @import './new-design.css';"
echo ""
echo "🚀 Now restart your frontend dev server:"
echo "   cd frontend"
echo "   npm run dev"
echo ""
