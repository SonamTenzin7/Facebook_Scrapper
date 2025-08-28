# 🚀 Cloud Automation Setup Guide

## ⚡ **Complete Cloud Automation - No Laptop Required!**

Your Facebook scraper will now run **entirely on GitHub Actions** every 4 hours, automatically scraping posts, updating your repository, and maintaining itself.

## 🔐 **Required: GitHub Secrets Setup**

### **Step 1: Set up FACEBOOK_CONFIG Secret**

1. **Go to your GitHub repository**: https://github.com/SonamTenzin7/Facebook_Scrapper
2. **Click Settings** (in the repository)
3. **Click "Secrets and variables"** → **"Actions"**
4. **Click "New repository secret"**
5. **Name**: `FACEBOOK_CONFIG`
6. **Value**: Copy your `config.json` content:

```json
{
  "facebook_page": "https://www.facebook.com/kuenselonline",
  "max_posts": 8,
  "delay_range": [2, 5],
  "headless": true,
  "timeout": 30
}
```

7. **Click "Add secret"**

### **Step 2: Enable GitHub Actions**
1. **Go to "Actions" tab** in your repository
2. **Enable Actions** if prompted
3. **Allow all actions and reusable workflows**

### **Step 3: Enable GitHub Pages** 
1. **Go to Settings** → **"Pages"**
2. **Source**: Deploy from a branch
3. **Branch**: `main` / `(root)`
4. **Click Save**

## 🤖 **What Happens Automatically**

### **Every 4 Hours, GitHub Actions Will:**
1. **🔄 Start a clean Ubuntu environment**
2. **📥 Download your latest code**
3. **🐍 Install Python and dependencies**
4. **🌐 Install Chrome browser**
5. **⚙️ Create config from your secret**
6. **🚀 Run the Facebook scraper**
7. **📊 Generate static API files**
8. **💾 Commit and push changes**
9. **🧹 Clean up old workflow runs**
10. **🌐 Deploy to GitHub Pages**

### **You Get:**
- ✅ **Fresh posts every 4 hours**
- ✅ **Automatic GitHub Pages updates**
- ✅ **Clean workflow run history**
- ✅ **Enhanced post validation**
- ✅ **No manual intervention needed**

## 📊 **Monitor Your Automation**

### **GitHub Actions Tab:**
- **View running workflows**: See real-time progress
- **Check logs**: Debug any issues
- **Manual trigger**: Run scraper on-demand
- **View history**: See all past runs

### **GitHub Pages:**
- **Live site**: https://SonamTenzin7.github.io/Facebook_Scrapper
- **Auto-updates**: Every time scraper runs
- **API endpoints**: JSON files automatically generated

### **Repository Updates:**
- **Automatic commits**: Every 4 hours (if new posts found)
- **Clean history**: Old workflow runs auto-deleted
- **Data files**: Always up-to-date

## ⚙️ **Advanced Configuration**

### **Change Frequency:**
Edit `.github/workflows/facebook-scraper.yml`:
```yaml
# Every 6 hours instead of 4:
- cron: '0 */6 * * *'

# Twice daily (9 AM and 9 PM):
- cron: '0 9,21 * * *'

# Once daily at 9 AM:
- cron: '0 9 * * *'
```

### **Adjust Posts Per Run:**
Modify the `FACEBOOK_CONFIG` secret:
```json
{
  "max_posts": 12
}
```

### **Manual Triggers:**
- **Go to Actions tab**
- **Click "Facebook Scraper - Cloud Automation"**
- **Click "Run workflow"**
- **Choose branch (main)**
- **Click "Run workflow"**

## 🔧 **Troubleshooting**

### **If Scraper Fails:**
1. **Check Actions tab** for error logs
2. **Verify FACEBOOK_CONFIG secret** is set correctly
3. **Check if Facebook changed their layout**
4. **Run manually** to test

### **If No Posts Found:**
- **Normal**: Sometimes Facebook has no new posts
- **Check logs**: Look for "No new posts found"
- **Manual test**: Trigger workflow manually

### **If Pages Don't Update:**
1. **Check Settings** → **Pages** is enabled
2. **Verify commits** are being made
3. **Wait a few minutes** for GitHub Pages to rebuild

## 🎯 **Success Indicators**

✅ **Green checkmarks** in Actions tab  
✅ **Regular commits** every 4 hours  
✅ **Updated GitHub Pages** site  
✅ **Fresh JSON API files**  
✅ **Clean workflow history** (<30 runs)

## 💡 **Pro Tips**

1. **Star your repo** - Easier to find
2. **Watch releases** - Get notifications
3. **Check weekly** - Monitor automation health
4. **Use manual triggers** - For testing
5. **Monitor GitHub Pages** - See your live data

Your scraper is now **100% automated in the cloud**! 🚀
