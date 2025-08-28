#!/bin/bash
# Kuensel Facebook Scraper - Smart Scheduler Launch Script

cd "$(dirname "$0")"

echo "Kuensel Facebook Scraper - Smart Monitoring"
echo "=============================================="

# Check Python dependencies
python3 -c "import selenium, requests" 2>/dev/null || {
    echo "Missing dependencies. Please install:"
    echo "   pip3 install selenium requests beautifulsoup4"
    exit 1
}

# Launch options
echo "Choose launch option:"
echo "1) Run monitoring dashboard"
echo "2) Start continuous smart scheduler"
echo "3) Run scraper once"
echo "4) Test notifications"
echo "5) Run historical recovery"
echo ""
read -p "Enter choice (1-5): " choice

case $choice in
    1)
        echo "Launching monitoring dashboard..."
        python3 monitoring_dashboard.py
        ;;
    2)
        echo "Starting continuous smart scheduler..."
        echo "Press Ctrl+C to stop"
        python3 smart_scheduler.py --continuous
        ;;
    3)
        echo "Running scraper once..."
        python3 facebook_scrapper.py
        ;;
    4)
        echo "Testing notifications..."
        python3 notification_system.py --test
        ;;
    5)
        echo "Running historical recovery..."
        python3 historical_recovery.py
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac
