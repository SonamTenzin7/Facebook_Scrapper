# 🤖 Kuensel Facebook Scraper - Cloud Automation

A fully automated Facebook scraper that collects posts from Kuensel's Facebook page and presents them through a clean API and web interface. **Now runs entirely in the cloud via GitHub Actions!**

## 🌐 Live Demo
- **Posts API**: [https://sonamtenzin7.github.io/Facebook_Scrapper/static_api/posts.json](https://sonamtenzin7.github.io/Facebook_Scrapper/static_api/posts.json)
- **Web Interface**: [https://sonamtenzin7.github.io/Facebook_Scrapper/](https://sonamtenzin7.github.io/Facebook_Scrapper/)

## ✨ Features

### 🚀 Cloud Automation
- ⚡ **100% cloud-based** - runs on GitHub Actions, no laptop needed
- 🕐 **Smart scheduling** - 4 times daily at optimal times (Bhutan timezone)
- 🧹 **Automatic cleanup** - intelligent workflow management
- 📊 **Repository maintenance** - automated optimization and health checks

### 📱 API & Interface
- 🔗 **JSON API** for easy integration with other applications
- 📊 Statistics dashboard showing total posts, images, and categories
- 🔍 Filter posts by category and content
- 📱 Responsive design for mobile and desktop
- 🖼️ Image gallery with click-to-expand
- ⚡ Static file generation for lightning-fast loading

### 🛡️ Reliability & Monitoring  
- 🔄 **Smart retry logic** and error handling
- 📈 **Performance monitoring** and optimization
- 🗑️ **Automatic cleanup** of old data and workflows
- 🔐 **Secure configuration** via GitHub Secrets

## 🚀 Cloud Setup (Recommended)

### Prerequisites
1. Fork this repository to your GitHub account
2. Enable GitHub Actions in your repository settings
3. Enable GitHub Pages for automated deployment

### Configuration
Add your Facebook configuration as a GitHub Secret:

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Create new secret: `FACEBOOK_CONFIG`
3. Add this JSON configuration:

```json
{
  "facebook_page": "https://www.facebook.com/kuenselonline",
  "max_posts": 8,
  "delay_range": [2, 5],
  "headless": true,
  "timeout": 30
}
```

### 🎯 That's it! 
The scraper will now run automatically every 6 hours and update your GitHub Pages site.

## 🛠️ Manual Operations

### Local Development
```bash
# Copy the example config for local testing
cp config/config.example.json config/config.json
# Edit config/config.json with your configuration
```

### Workflow Management
```bash
# Enhanced cleanup script
./scripts/enhanced_cleanup.sh

# Manual trigger specific workflows
gh workflow run facebook-scraper.yml
gh workflow run cleanup.yml
gh workflow run repository-maintenance.yml
```

## 📁 Project Structure

The project is now organized with a clean, professional structure:

```
📁 Facebook_Scrapper/
├── 📁 src/           # Python source code
├── 📁 scripts/       # Shell scripts & utilities  
├── 📁 config/        # Configuration files
├── 📁 web/           # Web interface files
├── 📁 docs/          # Documentation
├── 📁 data/          # Scraped data storage
├── 📁 log/           # Application logs
└── 📁 static_api/    # Generated API files
```

See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for detailed organization.

## 🧹 Repository Cleanup & Management

### Automated Cloud Workflows

| Workflow | Purpose | Schedule |
|----------|---------|----------|
| **Smart Workflow Deletion** | Intelligent cleanup based on patterns | Manual trigger only |
| **Repository Maintenance** | Daily optimization and health checks | Daily at 1 AM UTC |
| **Advanced Cleanup** | Bi-weekly comprehensive cleanup | Wed/Sun at 2 AM UTC |

### Manual Cleanup Options
Use the enhanced cleanup script for immediate control:

```bash
./enhanced_cleanup.sh
```

Features:
- 🧠 **Smart cleanup** - Removes old failed/cancelled runs intelligently
- 📅 **Date-based** - Clean by age (7, 14, 30 days)  
- 🎯 **Status-based** - Target specific run statuses
- 🔢 **Count-based** - Keep only N most recent runs
- ☢️ **Nuclear option** - Emergency cleanup (use with caution!)
- 📊 **Statistics** - Detailed analytics before/after cleanup

## 🔧 Architecture

### Cloud Automation Flow
```
GitHub Actions (Every 6 hours)
    ↓
🌐 Chrome Browser (Ubuntu)
    ↓  
🕷️ Scrape Kuensel Facebook
    ↓
📊 Generate Static API
    ↓
📤 Update GitHub Repository
    ↓
🚀 Deploy to GitHub Pages
```

### File Structure
```
├── .github/workflows/          # Cloud automation workflows
│   ├── facebook-scraper.yml   # Main scraping automation
│   ├── cleanup.yml            # Advanced workflow cleanup
│   ├── repository-maintenance.yml  # Daily maintenance
│   └── smart-workflow-deletion.yml # Manual cleanup tool
├── data/                      # Scraped data storage
├── static_api/               # Generated API files
├── log/                      # Application logs
├── enhanced_cleanup.sh       # Advanced cleanup script
└── facebook_scrapper.py      # Core scraping engine
```

## 🚀 How It Works
1. **Automation**: macOS launch agent runs the scraper every hour
2. **Data Collection**: Selenium WebDriver scrapes Kuensel's Facebook page
3. **Smart Storage**: New posts are added to a single master file (no duplicates)
4. **Static Generation**: JSON API files are created in `static_api/` directory
5. **Display**: Frontend loads data from static files for fast, serverless operation

## File Structure
```
├── frontend.html              # Main web interface
├── facebook_scrapper.py       # Core scraper script
├── generate_static_api.py     # Static API file generator
├── view_posts.sh             # Local viewer launcher
├── com.facebook.scraper.plist # Launch agent configuration
├── static_api/               # Generated API files
│   ├── posts.json
│   ├── categories.json
│   ├── stats.json
│   └── posts_general.json
└── data/                     # Scraped data storage
    ├── kuensel_posts_master.json  # Master file with all posts
    └── last_run.txt              # Tracks last scraping time
```

## GitHub Pages Setup
This repository is configured to automatically deploy to GitHub Pages, updating hourly with new posts.

## Requirements
- Python 3.7+
- Chrome/Chromium browser
- macOS (for launch agent automation)

## Dependencies
```bash
pip install -r requirements.txt
```

## 🔒 Security Notice
- `config.json` contains sensitive credentials and is excluded from the repository
- Copy `config.example.json` to `config.json` and add your credentials
- Never commit `config.json` to version control
