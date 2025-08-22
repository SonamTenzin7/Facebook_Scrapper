#!/bin/bash

# Quick Workflow Cleanup Test
# This shows what option 3 (Keep only last 50 successful runs) would do

echo "🧹 Testing Workflow Cleanup - Option 3"
echo "======================================"

# Check if GitHub CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed."
    exit 1
fi

# Check if user is logged in
if ! gh auth status &> /dev/null; then
    echo "🔐 Please complete GitHub CLI login first:"
    echo "   gh auth login"
    echo ""
    echo "📋 What Option 3 would do:"
    echo "1. List all successful workflow runs"
    echo "2. Keep the first 50 (most recent)"
    echo "3. Delete runs 51+ (older ones)"
    echo ""
    echo "💡 This helps maintain a clean history while preserving recent successful runs"
    exit 1
fi

echo "📊 Current workflow runs analysis:"
echo ""

# Show current status
echo "🔍 Total workflow runs:"
total_runs=$(gh run list --json databaseId --jq '. | length')
echo "   Total: $total_runs runs"

echo ""
echo "🔍 Successful workflow runs:"
success_runs=$(gh run list --status success --json databaseId --jq '. | length')
echo "   Successful: $success_runs runs"

if [ $success_runs -gt 50 ]; then
    to_delete=$((success_runs - 50))
    echo "   ✂️  Would delete: $to_delete old successful runs"
    echo "   ✅ Would keep: 50 most recent successful runs"
else
    echo "   ✅ No cleanup needed - you have $success_runs successful runs (≤50)"
fi

echo ""
echo "🔍 Failed/Cancelled workflow runs:"
failed_runs=$(gh run list --status failure --json databaseId --jq '. | length' 2>/dev/null || echo "0")
cancelled_runs=$(gh run list --status cancelled --json databaseId --jq '. | length' 2>/dev/null || echo "0")
echo "   Failed: $failed_runs runs"
echo "   Cancelled: $cancelled_runs runs"

echo ""
echo "💡 Recommendation:"
if [ $total_runs -gt 100 ]; then
    echo "   🚨 You have $total_runs total runs - cleanup recommended!"
elif [ $total_runs -gt 50 ]; then
    echo "   ⚠️  You have $total_runs total runs - consider cleanup"
else
    echo "   ✅ You have $total_runs total runs - manageable"
fi

echo ""
echo "🔧 To actually run the cleanup, use:"
echo "   ./cleanup_workflows.sh"
