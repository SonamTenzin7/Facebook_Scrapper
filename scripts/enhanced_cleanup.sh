#!/bin/bash

# 🧹 Enhanced Workflow Cleanup Tool
# This script helps remove old workflow runs to keep your repository clean and optimized

set -e

# Colors for pretty output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧹 Enhanced GitHub Workflow Cleanup Tool${NC}"
echo -e "${BLUE}===========================================${NC}"
echo ""

# Check if GitHub CLI is installed
if ! command -v gh &> /dev/null; then
    echo -e "${RED}❌ GitHub CLI not found!${NC}"
    echo -e "${YELLOW}📦 Install it first:${NC}"
    echo "   macOS: brew install gh"
    echo "   Linux: sudo apt install gh"
    echo "   Windows: winget install GitHub.cli"
    echo ""
    echo -e "${YELLOW}Then login: gh auth login${NC}"
    exit 1
fi

# Check if user is authenticated
if ! gh auth status &> /dev/null; then
    echo -e "${RED}❌ Not authenticated with GitHub!${NC}"
    echo -e "${YELLOW}🔐 Login first: gh auth login${NC}"
    exit 1
fi

# Get repository info
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null || echo "unknown")
echo -e "${GREEN}📂 Repository: $REPO${NC}"

# Get current workflow stats
echo -e "${BLUE}🔍 Analyzing current workflows...${NC}"
TOTAL_RUNS=$(gh run list --limit 1000 --json databaseId | jq length)
SUCCESS_RUNS=$(gh run list --limit 1000 --json conclusion | jq '[.[] | select(.conclusion=="success")] | length')
FAILED_RUNS=$(gh run list --limit 1000 --json conclusion | jq '[.[] | select(.conclusion=="failure")] | length')
CANCELLED_RUNS=$(gh run list --limit 1000 --json conclusion | jq '[.[] | select(.conclusion=="cancelled")] | length')

echo -e "${PURPLE}📊 Current Statistics:${NC}"
echo "   📈 Total runs: $TOTAL_RUNS"
echo "   ✅ Successful: $SUCCESS_RUNS"  
echo "   ❌ Failed: $FAILED_RUNS"
echo "   ⏹️  Cancelled: $CANCELLED_RUNS"
echo ""

# Cleanup menu
echo -e "${YELLOW}🎯 Choose cleanup strategy:${NC}"
echo "1. 🧠 Smart cleanup (recommended)"
echo "2. 📅 Delete runs older than 7 days"
echo "3. 📅 Delete runs older than 14 days"
echo "4. 📅 Delete runs older than 30 days"
echo "5. ❌ Delete all failed runs"
echo "6. ⏹️  Delete all cancelled runs"
echo "7. 🔢 Keep only last 20 runs"
echo "8. 🔢 Keep only last 50 runs"
echo "9. ☢️  Nuclear option (keep only last 5)"
echo "10. 📊 Show detailed statistics only"
echo "0. ❌ Exit"
echo ""

read -p "Enter your choice (0-10): " choice

case $choice in
    1)
        echo -e "${GREEN}🧠 Executing smart cleanup...${NC}"
        echo "   • Deleting failed runs older than 3 days"
        echo "   • Deleting cancelled runs (keep last 5)"
        echo "   • Keeping last 20 successful runs"
        echo ""
        
        # Delete old failed runs
        echo -e "${YELLOW}Phase 1: Old failed runs...${NC}"
        three_days_ago=$(date -d '3 days ago' '+%Y-%m-%d' 2>/dev/null || date -v-3d '+%Y-%m-%d')
        gh run list --status failure --created-before "$three_days_ago" --json databaseId -q '.[].databaseId' | \
        while read run_id; do
            [ ! -z "$run_id" ] && gh run delete $run_id && echo "🗑️  Deleted failed run: $run_id"
        done
        
        # Delete most cancelled runs
        echo -e "${YELLOW}Phase 2: Cancelled runs...${NC}"
        gh run list --status cancelled --limit 100 --json databaseId -q '.[5:] | .[].databaseId' | \
        while read run_id; do
            [ ! -z "$run_id" ] && gh run delete $run_id && echo "🗑️  Deleted cancelled run: $run_id"
        done
        
        # Keep only last 30 successful runs
        echo -e "${YELLOW}Phase 3: Old successful runs...${NC}"
        gh run list --status success --limit 100 --json databaseId -q '.[30:] | .[].databaseId' | \
        while read run_id; do
            [ ! -z "$run_id" ] && gh run delete $run_id && echo "🗑️  Deleted old successful run: $run_id"
        done
        ;;
        
    2)
        echo -e "${GREEN}📅 Deleting workflow runs older than 7 days...${NC}"
        seven_days_ago=$(date -d '7 days ago' '+%Y-%m-%d' 2>/dev/null || date -v-7d '+%Y-%m-%d')
        gh run list --created-before "$seven_days_ago" --json databaseId -q '.[].databaseId' | \
        while read run_id; do
            [ ! -z "$run_id" ] && gh run delete $run_id && echo "🗑️  Deleted run: $run_id"
        done
        ;;
        
    3)
        echo -e "${GREEN}📅 Deleting workflow runs older than 14 days...${NC}"
        fourteen_days_ago=$(date -d '14 days ago' '+%Y-%m-%d' 2>/dev/null || date -v-14d '+%Y-%m-%d')
        gh run list --created-before "$fourteen_days_ago" --json databaseId -q '.[].databaseId' | \
        while read run_id; do
            [ ! -z "$run_id" ] && gh run delete $run_id && echo "🗑️  Deleted run: $run_id"
        done
        ;;
        
    4)
        echo -e "${GREEN}📅 Deleting workflow runs older than 30 days...${NC}"
        thirty_days_ago=$(date -d '30 days ago' '+%Y-%m-%d' 2>/dev/null || date -v-30d '+%Y-%m-%d')
        gh run list --created-before "$thirty_days_ago" --json databaseId -q '.[].databaseId' | \
        while read run_id; do
            [ ! -z "$run_id" ] && gh run delete $run_id && echo "🗑️  Deleted run: $run_id"
        done
        ;;
        
    5)
        echo -e "${GREEN}❌ Deleting all failed workflow runs...${NC}"
        gh run list --status failure --json databaseId -q '.[].databaseId' | \
        while read run_id; do
            [ ! -z "$run_id" ] && gh run delete $run_id && echo "🗑️  Deleted failed run: $run_id"
        done
        ;;
        
    6)
        echo -e "${GREEN}⏹️  Deleting all cancelled workflow runs...${NC}"
        gh run list --status cancelled --json databaseId -q '.[].databaseId' | \
        while read run_id; do
            [ ! -z "$run_id" ] && gh run delete $run_id && echo "🗑️  Deleted cancelled run: $run_id"
        done
        ;;
        
    7)
        echo -e "${GREEN}🔢 Keeping only last 20 runs...${NC}"
        gh run list --limit 1000 --json databaseId -q '.[20:] | .[].databaseId' | \
        while read run_id; do
            [ ! -z "$run_id" ] && gh run delete $run_id && echo "🗑️  Deleted run: $run_id"
        done
        ;;
        
    8)
        echo -e "${GREEN}🔢 Keeping only last 50 runs...${NC}"
        gh run list --limit 1000 --json databaseId -q '.[50:] | .[].databaseId' | \
        while read run_id; do
            [ ! -z "$run_id" ] && gh run delete $run_id && echo "🗑️  Deleted run: $run_id"
        done
        ;;
        
    9)
        echo -e "${RED}☢️  WARNING: Nuclear option selected!${NC}"
        echo -e "${RED}This will delete almost all workflow history!${NC}"
        echo -e "${YELLOW}Only the last 5 runs will be kept.${NC}"
        echo ""
        read -p "Are you absolutely sure? Type 'NUCLEAR' to confirm: " confirm
        
        if [ "$confirm" = "NUCLEAR" ]; then
            echo -e "${RED}🚀 Executing nuclear cleanup...${NC}"
            gh run list --limit 1000 --json databaseId -q '.[5:] | .[].databaseId' | \
            while read run_id; do
                [ ! -z "$run_id" ] && gh run delete $run_id && echo "💥 Deleted run: $run_id"
            done
        else
            echo -e "${YELLOW}❌ Nuclear cleanup cancelled.${NC}"
            exit 0
        fi
        ;;
        
    10)
        echo -e "${BLUE}📊 Detailed Workflow Statistics${NC}"
        echo -e "${BLUE}================================${NC}"
        
        # Get detailed stats
        gh run list --limit 1000 --json conclusion,status,createdAt,name | \
        jq -r '
        group_by(.conclusion) | 
        map({
            conclusion: .[0].conclusion // "in_progress",
            count: length
        }) | 
        sort_by(.count) | 
        reverse | 
        .[] | 
        "\(.conclusion): \(.count)"
        ' | while read line; do
            echo "   📈 $line"
        done
        
        # Recent activity
        echo ""
        echo -e "${PURPLE}🕐 Recent Activity (last 10 runs):${NC}"
        gh run list --limit 10 --json conclusion,name,createdAt | \
        jq -r '.[] | "\(.createdAt) | \(.conclusion) | \(.name)"' | \
        while IFS='|' read date conclusion name; do
            case $conclusion in
                success) icon="✅" ;;
                failure) icon="❌" ;;
                cancelled) icon="⏹️" ;;
                *) icon="🔄" ;;
            esac
            echo "   $icon $(echo $date | cut -d'T' -f1) - $(echo $name | tr -d ' ')"
        done
        
        # Workflow names
        echo ""
        echo -e "${PURPLE}📋 Workflow Types:${NC}"
        gh run list --limit 100 --json name | jq -r '.[].name' | sort | uniq -c | sort -nr | \
        while read count name; do
            echo "   🔧 $name: $count runs"
        done
        
        exit 0
        ;;
        
    0)
        echo -e "${YELLOW}❌ Cleanup cancelled. Goodbye!${NC}"
        exit 0
        ;;
        
    *)
        echo -e "${RED}❌ Invalid choice. Please try again.${NC}"
        exit 1
        ;;
esac

# Wait a moment for API to update
echo -e "${BLUE}⏳ Waiting for GitHub API to update...${NC}"
sleep 5

# Show results
echo ""
echo -e "${GREEN}✅ Cleanup completed!${NC}"

# Get new stats
NEW_TOTAL=$(gh run list --limit 1000 --json databaseId | jq length)
DELETED=$((TOTAL_RUNS - NEW_TOTAL))
PERCENTAGE=$((DELETED * 100 / TOTAL_RUNS))

echo -e "${PURPLE}📊 Cleanup Summary:${NC}"
echo "   📉 Runs before: $TOTAL_RUNS"
echo "   📈 Runs after: $NEW_TOTAL" 
echo "   🗑️  Deleted: $DELETED runs"
echo "   📊 Reduction: ${PERCENTAGE}%"
echo "   💾 Est. space saved: $((DELETED * 2))MB"

echo ""
echo -e "${GREEN}🎉 Repository cleanup successful!${NC}"
echo -e "${BLUE}💡 Tip: Run this script regularly to keep your repository optimized.${NC}"
