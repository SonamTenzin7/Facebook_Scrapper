# Kuensel Facebook Scraper

An automated Facebook scraper that collects posts from Kuensel's Facebook page and presents them in a clean, filterable web interface.

## 🌐 Live Demo
View the latest posts: [https://sonamtenzin.github.io/Facebook_Scrapper/](https://yourusername.github.io/Facebook_Scrapper/)

## Features
- ✅ Automated scraping every hour via macOS launch agent
- 📊 Statistics dashboard showing total posts, images, and categories
- 🔍 Filter posts by category
- 📱 Responsive design for mobile and desktop
- 🖼️ Image gallery with click-to-expand
- ⚡ Static file generation for fast loading
- 🔄 Auto-refresh every 5 minutes

## Quick Start

### View Posts Locally
```bash
./view_posts.sh
```

### Manual Scraping
```bash
python3 facebook_scrapper.py
```

## How It Works
1. **Automation**: macOS launch agent runs the scraper every hour
2. **Data Collection**: Selenium WebDriver scrapes Kuensel's Facebook page
3. **Processing**: Posts are categorized and processed into JSON files
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
└── data/                     # Raw scraped data
    └── kuensel_posts_*.json
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
