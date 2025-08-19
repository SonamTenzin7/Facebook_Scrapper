#!/bin/bash

# Auto-commit and push updated static API files to GitHub
# This script is called after successful scraping

cd "$(dirname "$0")"

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "⚠️  Not a git repository. Initialize with: git init"
    exit 1
fi

# Check if there are changes to commit
if git diff --quiet static_api/ && git diff --cached --quiet static_api/; then
    echo "📊 No changes in static API files"
    exit 0
fi

# Get current timestamp
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

echo "📤 Committing updated static API files..."

# Add static API files
git add static_api/

# Commit with timestamp
git commit -m "🔄 Auto-update static API files - $TIMESTAMP"

# Push to remote (suppress output for security)
echo "🚀 Pushing to GitHub..."
if git push origin main > /dev/null 2>&1 || git push origin master > /dev/null 2>&1; then
    echo "✅ Successfully pushed to GitHub Pages"
    echo "🌐 Site will update automatically in a few minutes"
else
    echo "❌ Failed to push to GitHub"
    echo "💡 Make sure your repository is set up and you have push access"
fi
