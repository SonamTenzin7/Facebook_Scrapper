# GitHub Workflow Management Guide

## 🚨 Problem: Too Many Workflow Runs

Your Facebook scraper was running **every 30 minutes**, creating ~1,440 workflow runs per month!

## ✅ Solutions Implemented

### 1. **Reduced Frequency**
- **Before**: Every 30 minutes (48 runs/day)  
- **After**: Every 4 hours (6 runs/day)
- **Savings**: 87% reduction in workflow runs!

### 2. **Automatic Cleanup**
- Added cleanup step to main workflow
- Keeps only last 30 runs automatically
- Runs weekly cleanup on Sundays

### 3. **Manual Cleanup Tool**
Use the `cleanup_workflows.sh` script for immediate cleanup:

```bash
# Run the cleanup tool
./cleanup_workflows.sh
```

**Prerequisites**: Install GitHub CLI first:
```bash
# macOS
brew install gh

# Then login
gh auth login
```

### 4. **GitHub CLI Commands**
Direct commands for manual cleanup:

```bash
# List current runs
gh run list --limit 20

# Delete all failed runs
gh run list --status failure --json databaseId --jq '.[].databaseId' | xargs -I {} gh api repos/OWNER/REPO/actions/runs/{} -X DELETE

# Delete runs older than 30 days (approximate)
gh run list --json databaseId --jq '.[50:] | .[].databaseId' | xargs -I {} gh api repos/OWNER/REPO/actions/runs/{} -X DELETE

# Delete specific run by ID
gh api repos/OWNER/REPO/actions/runs/RUN_ID -X DELETE
```

## 📊 Recommended Schedule Options

Choose based on your needs:

| Frequency | Cron Expression | Daily Runs | Use Case |
|-----------|----------------|------------|-----------|
| Every 4 hours | `0 */4 * * *` | 6 | ✅ **Current** - Balanced |
| Every 6 hours | `0 */6 * * *` | 4 | Good for stable content |
| Every 8 hours | `0 */8 * * *` | 3 | Light monitoring |
| Twice daily | `0 9,21 * * *` | 2 | Minimal runs |
| Daily | `0 9 * * *` | 1 | Very light usage |

## 🎯 Current Setup Summary

✅ **Workflow frequency**: Every 4 hours  
✅ **Auto-cleanup**: Keeps last 30 runs  
✅ **Weekly cleanup**: Sundays at 2 AM  
✅ **Manual cleanup**: `cleanup_workflows.sh` script  

## 💡 Pro Tips

1. **Monitor your usage**: Check GitHub Actions tab regularly
2. **Adjust frequency**: Modify the cron expression if needed
3. **Use manual triggers**: Use `workflow_dispatch` for testing
4. **Set up notifications**: Get alerts for failed runs only

## 🔧 Quick Fixes

**Change workflow frequency:**
Edit `.github/workflows/facebook-scraper.yml` and modify the cron expression.

**Immediate cleanup:**
```bash
./cleanup_workflows.sh
```

**Check current status:**
```bash
gh run list --limit 10
```
