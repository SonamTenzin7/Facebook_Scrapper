#!/bin/bash

# GitHub Workflow Cleanup Script
# This script helps remove old workflow runs to keep your repository clean

echo "🧹 GitHub Workflow Cleanup Tool"
echo "================================="

# Check if GitHub CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed."
    echo "📥 Install it first:"
    echo "   macOS: brew install gh"
    echo "   Or download from: https://cli.github.com/"
    exit 1
fi

# Check if user is logged in
if ! gh auth status &> /dev/null; then
    echo "🔐 Please log in to GitHub CLI first:"
    echo "   gh auth login"
    exit 1
fi

echo "📊 Current workflow runs:"
gh run list --limit 10

echo ""
echo "🗂️  Available cleanup options:"
echo "1. Delete all workflow runs older than 30 days"
echo "2. Delete all workflow runs older than 7 days" 
echo "3. Keep only last 50 successful runs"
echo "4. Delete all failed/cancelled runs"
echo "5. Delete specific workflow runs by status"
echo "6. Show detailed cleanup commands (manual)"

read -p "Choose option (1-6): " choice

case $choice in
    1)
        echo "🗑️  Deleting workflow runs older than 30 days..."
        gh run list --json databaseId --jq '.[100:] | .[].databaseId' | head -50 | xargs -I {} gh api repos/SonamTenzin7/Facebook_Scrapper/actions/runs/{} -X DELETE
        ;;
    2)
        echo "🗑️  Deleting workflow runs older than 7 days..."
        # Get runs older than 7 days and delete them
        gh run list --json databaseId,createdAt --jq '.[] | select(.createdAt < (now - 604800)) | .databaseId' | head -50 | xargs -I {} gh api repos/SonamTenzin7/Facebook_Scrapper/actions/runs/{} -X DELETE
        ;;
    3)
        echo "🗑️  Keeping only last 50 successful runs..."
        gh run list --status success --json databaseId --jq '.[50:] | .[].databaseId' | xargs -I {} gh api repos/SonamTenzin7/Facebook_Scrapper/actions/runs/{} -X DELETE
        ;;
    4)
        echo "🗑️  Deleting all failed/cancelled runs..."
        gh run list --status failure --json databaseId --jq '.[].databaseId' | xargs -I {} gh api repos/SonamTenzin7/Facebook_Scrapper/actions/runs/{} -X DELETE
        gh run list --status cancelled --json databaseId --jq '.[].databaseId' | xargs -I {} gh api repos/SonamTenzin7/Facebook_Scrapper/actions/runs/{} -X DELETE
        ;;
    5)
        echo "Available statuses: success, failure, cancelled, in_progress, queued"
        read -p "Enter status to delete: " status
        echo "🗑️  Deleting all $status runs..."
        gh run list --status $status --json databaseId --jq '.[].databaseId' | xargs -I {} gh api repos/SonamTenzin7/Facebook_Scrapper/actions/runs/{} -X DELETE
        ;;
    6)
        echo "📋 Manual cleanup commands:"
        echo ""
        echo "# List all runs:"
        echo "gh run list --limit 100"
        echo ""
        echo "# Delete specific run by ID:"
        echo "gh api repos/SonamTenzin7/Facebook_Scrapper/actions/runs/RUN_ID -X DELETE"
        echo ""
        echo "# Delete all failed runs:"
        echo "gh run list --status failure --json databaseId --jq '.[].databaseId' | xargs -I {} gh api repos/SonamTenzin7/Facebook_Scrapper/actions/runs/{} -X DELETE"
        echo ""
        echo "# Delete runs older than specific date (manual filter needed):"
        echo "gh run list --json databaseId,createdAt --jq '.[]'"
        ;;
    *)
        echo "❌ Invalid option"
        exit 1
        ;;
esac

echo "✅ Cleanup completed!"
echo "📊 Current status:"
gh run list --limit 5
