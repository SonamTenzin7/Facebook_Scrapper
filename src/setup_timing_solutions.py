#!/usr/bin/env python3
"""
Setup Script for Comprehensive Timing Solutions
Sets up all monitoring and notification systems
"""

import os
import json
import subprocess
import sys

def create_notification_config():
    """Create notification configuration file"""
    config = {
        "email": {
            "enabled": False,
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "sender_email": "your-email@gmail.com",
            "sender_password": "your-app-password",  # Use App Password, not regular password
            "recipient_email": "your-email@gmail.com",
            "app_password": ""  # Google App Password for enhanced security
        },
        "webhook": {
            "enabled": False,
            "url": "",
            "discord_webhook": "https://discord.com/api/webhooks/YOUR_WEBHOOK_URL",
            "slack_webhook": "https://hooks.slack.com/services/YOUR_WEBHOOK_URL"
        }
    }
    
    config_file = "notification_config.json"
    if not os.path.exists(config_file):
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"✅ Created {config_file}")
        print("💡 Edit this file to enable email/webhook notifications")
    else:
        print(f"ℹ️  {config_file} already exists")

def create_scheduler_config():
    """Create scheduler configuration file"""
    config = {
        "scraping": {
            "peak_hours": [9, 10, 11, 12, 13, 14, 15, 16, 17, 18],
            "peak_interval": 1800,      # 30 minutes
            "normal_interval": 3600,    # 1 hour
            "night_interval": 7200,     # 2 hours
            "min_interval": 900         # 15 minutes minimum
        },
        "monitoring": {
            "enabled": True,
            "check_interval": 300,      # 5 minutes
            "rss_check": True,
            "page_change_detection": True
        },
        "recovery": {
            "enabled": True,
            "daily_recovery_hour": 4,   # 4 AM
            "weekly_deep_recovery": 0,  # Sunday
            "max_recovery_posts": 50
        },
        "notifications": {
            "on_new_posts": True,
            "on_errors": True,
            "on_recovery": True,
            "daily_summary": True,
            "summary_hour": 19          # 7 PM
        }
    }
    
    config_file = "scheduler_config.json"
    if not os.path.exists(config_file):
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"✅ Created {config_file}")
    else:
        print(f"ℹ️  {config_file} already exists")

def create_launch_scripts():
    """Create convenient launch scripts"""
    
    # macOS launch script
    launch_script = """#!/bin/bash
# Kuensel Facebook Scraper - Smart Scheduler Launch Script

cd "$(dirname "$0")"

echo "🚀 Kuensel Facebook Scraper - Smart Monitoring"
echo "=============================================="

# Check Python dependencies
python3 -c "import selenium, requests" 2>/dev/null || {
    echo "❌ Missing dependencies. Please install:"
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
        echo "📊 Launching monitoring dashboard..."
        python3 monitoring_dashboard.py
        ;;
    2)
        echo "🔄 Starting continuous smart scheduler..."
        echo "Press Ctrl+C to stop"
        python3 smart_scheduler.py --continuous
        ;;
    3)
        echo "🚀 Running scraper once..."
        python3 facebook_scrapper.py
        ;;
    4)
        echo "🧪 Testing notifications..."
        python3 notification_system.py --test
        ;;
    5)
        echo "🏛️ Running historical recovery..."
        python3 historical_recovery.py
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac
"""
    
    with open("launch_scraper.sh", "w") as f:
        f.write(launch_script)
    
    # Make executable
    os.chmod("launch_scraper.sh", 0o755)
    print("✅ Created launch_scraper.sh")
    
    # Create simple run script for cron
    cron_script = """#!/bin/bash
cd "$(dirname "$0")"
python3 smart_scheduler.py --once >> log/scheduler.log 2>&1
"""
    
    with open("run_smart_scheduler.sh", "w") as f:
        f.write(cron_script)
    
    os.chmod("run_smart_scheduler.sh", 0o755)
    print("✅ Created run_smart_scheduler.sh")

def setup_log_directory():
    """Ensure log directory exists"""
    os.makedirs("log", exist_ok=True)
    print("✅ Log directory ready")

def show_setup_instructions():
    """Show post-setup instructions"""
    print("\n" + "="*60)
    print("🎉 SETUP COMPLETE!")
    print("="*60)
    print()
    print("📋 NEXT STEPS:")
    print()
    print("1️⃣  Configure Notifications (Optional):")
    print("   • Edit notification_config.json")
    print("   • Add your email/webhook settings")
    print("   • Test with: python3 notification_system.py --test")
    print()
    print("2️⃣  Choose Your Running Method:")
    print()
    print("🖥️  INTERACTIVE (Recommended for testing):")
    print("   ./launch_scraper.sh")
    print()
    print("🤖 AUTOMATED (Recommended for production):")
    print("   python3 smart_scheduler.py --continuous")
    print()
    print("📊 MONITORING:")
    print("   python3 monitoring_dashboard.py")
    print("   python3 monitoring_dashboard.py --monitor")
    print()
    print("3️⃣  GitHub Actions Enhancement:")
    print("   Your GitHub Actions are already enhanced to run every 30 minutes")
    print("   This local smart scheduler provides additional intelligence")
    print()
    print("4️⃣  Cron Setup (Alternative to continuous mode):")
    print("   Add to crontab: */5 * * * * /path/to/run_smart_scheduler.sh")
    print()
    print("="*60)
    print("💡 FEATURES READY:")
    print("✅ Enhanced GitHub Actions (30-min intervals)")
    print("✅ Adaptive rate limiting (15min-2hr based on activity)")
    print("✅ Historical recovery system")
    print("✅ Smart monitoring with RSS/page change detection")
    print("✅ Comprehensive notification system")
    print("✅ Real-time monitoring dashboard")
    print("✅ Intelligent scheduling based on Bhutan time zones")
    print("="*60)

def main():
    """Main setup function"""
    print("🚀 Setting up Kuensel Facebook Scraper - Comprehensive Timing Solutions")
    print("="*80)
    
    # Create configuration files
    create_notification_config()
    create_scheduler_config()
    
    # Setup directories and scripts
    setup_log_directory()
    create_launch_scripts()
    
    # Show final instructions
    show_setup_instructions()

if __name__ == "__main__":
    main()
