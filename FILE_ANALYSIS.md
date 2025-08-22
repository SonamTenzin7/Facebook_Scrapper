# File Usage Analysis - Facebook Scrapper

## ✅ REMOVED FILES (Unnecessary):
- `api-test.html` - Empty file
- `view_posts.sh` - Replaced by frontend.html
- `post_monitor.py` - Functionality replaced by smart_scheduler.py
- `__pycache__/` - Python cache directory
- `.DS_Store` - macOS system file

## 🔑 CORE FILES (Essential):
- `facebook_scrapper.py` - Main scraper engine ⭐
- `requirements.txt` - Python dependencies
- `config.json` / `config.example.json` - Configuration
- `data/kuensel_posts_master.json` - Main data storage

## 🚀 AUTOMATION FILES (Important):
- `smart_scheduler.py` - Intelligent scheduling system
- `run_scraper.sh` - Main execution script
- `launch_scraper.sh` - Interactive launcher
- `auto_deploy.sh` - GitHub deployment
- `com.facebook.scraper.plist` - macOS automation

## 🌐 WEB INTERFACE (For GitHub Pages):
- `index.html` - Entry point (redirects to frontend)
- `frontend.html` - Main web interface
- `api.py` - API server
- `generate_static_api.py` - Static JSON API generator
- `static_api/` - Generated API files

## 📊 MONITORING & NOTIFICATIONS:
- `monitoring_dashboard.py` - System monitoring
- `notification_system.py` - Alerts and notifications
- `notification_config.json` - Notification settings
- `historical_recovery.py` - Data recovery tools

## 🔧 SETUP & CONFIGURATION:
- `setup_github.sh` - Initial GitHub setup
- `setup_timing_solutions.py` - Scheduling configuration
- `scheduler_config.json` - Scheduler settings
- `run_smart_scheduler.sh` - Scheduler runner
- `clean_logs.sh` - Log maintenance

## 📚 DOCUMENTATION:
- `README.md` - Main documentation
- `API_DOCS.md` - API documentation  
- `TIMING_SOLUTIONS.md` - Scheduling documentation

## 📁 DIRECTORIES:
- `.github/workflows/` - GitHub Actions
- `log/` - Application logs
- `data/` - Scraped data storage
- `static_api/` - Generated API files

## 🎯 MINIMAL SETUP (If you want the simplest version):
You could run with just these core files:
- `facebook_scrapper.py`
- `requirements.txt`
- `config.json`
- `data/` directory

The rest add automation, monitoring, and web interface features.
