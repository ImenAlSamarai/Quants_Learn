#!/bin/bash

# Helper script for adding new content
# Usage: ./scripts/add-content.sh <file> <category>

if [ $# -ne 2 ]; then
  echo "Usage: ./scripts/add-content.sh <file> <category>"
  echo ""
  echo "Examples:"
  echo "  ./scripts/add-content.sh ~/Downloads/book.pdf statistics"
  echo "  ./scripts/add-content.sh notes.md machine_learning"
  echo ""
  echo "Valid categories:"
  echo "  - linear_algebra"
  echo "  - calculus"
  echo "  - probability"
  echo "  - statistics"
  echo "  - machine_learning"
  echo "  - finance"
  echo "  - trading"
  exit 1
fi

FILE=$1
CATEGORY=$2

# Validate file exists
if [ ! -f "$FILE" ]; then
  echo "❌ Error: File not found: $FILE"
  exit 1
fi

# Validate category exists
TARGET_DIR="content/$CATEGORY"
if [ ! -d "$TARGET_DIR" ]; then
  echo "❌ Error: Category directory not found: $TARGET_DIR"
  echo ""
  echo "Valid categories:"
  ls -d content/*/ | sed 's/content\///g' | sed 's/\///g' | sed 's/^/  - /'
  exit 1
fi

# Get filename
FILENAME=$(basename "$FILE")

echo "=================================="
echo "   ADDING CONTENT"
echo "=================================="
echo ""
echo "File: $FILENAME"
echo "Category: $CATEGORY"
echo "Target: $TARGET_DIR/$FILENAME"
echo ""

# Check if file already exists
if [ -f "$TARGET_DIR/$FILENAME" ]; then
  echo "⚠️  File already exists. Overwrite?"
  read -p "Continue? (y/n) " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
  fi
fi

# Copy file
echo "📋 Copying file..."
cp "$FILE" "$TARGET_DIR/$FILENAME"

if [ $? -eq 0 ]; then
  echo "   ✅ File copied successfully"
else
  echo "   ❌ Failed to copy file"
  exit 1
fi

# Get file size
SIZE=$(du -h "$TARGET_DIR/$FILENAME" | cut -f1)
echo "   Size: $SIZE"
echo ""

# Index content
echo "🔍 Indexing content..."
cd backend
python scripts/index_content.py --content-dir ../content 2>&1 | grep -E "(Found|Extracted|Created|✓|✗|Error)" || echo "   (Check backend logs for details)"

if [ $? -eq 0 ]; then
  echo "   ✅ Content indexed successfully"
else
  echo "   ⚠️  Indexing may have had issues (check logs)"
fi
cd ..
echo ""

# Check database update
echo "💾 Verifying database update..."
cd backend
CHUNK_COUNT=$(python setup.py --status | grep "Content Chunks:" | awk '{print $3}')
echo "   Content Chunks: $CHUNK_COUNT"
cd ..
echo ""

# Git commit
echo "📝 Creating git commit..."
git add "$TARGET_DIR/$FILENAME"

COMMIT_MSG="Add $FILENAME to $CATEGORY content

- File: $FILENAME ($SIZE)
- Category: $CATEGORY
- Auto-committed by add-content.sh"

git commit -m "$COMMIT_MSG"

if [ $? -eq 0 ]; then
  echo "   ✅ Git commit created"
else
  echo "   ⚠️  Git commit failed (manual commit needed)"
fi
echo ""

# Summary
echo "=================================="
echo "✅ Content addition complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "  1. Test learning path generation:"
echo "     cd backend"
echo "     python scripts/test_learning_path.py --job \"<relevant job>\""
echo ""
echo "  2. Push to remote:"
echo "     git push origin develop"
echo ""
echo "  3. Update CURRENT_STATE.md"
echo ""
