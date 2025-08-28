"""
Smart Scheduler for Kuensel Facebook Scraper
Intelligently runs scraping, monitoring, and recovery based on optimal timing
"""

import time
import json
import os
import subprocess
from datetime import datetime, timedelta
from notification_system import NotificationSystem
from post_monitor import PostMonitor
from monitoring_dashboard import MonitoringDashboard

class SmartScheduler:
    def __init__(self):
        self.notifier = NotificationSystem()
        self.post_monitor = PostMonitor()
        self.dashboard = MonitoringDashboard()
        self.config = self.load_scheduler_config()
        
    def load_scheduler_config(self):
        """Load scheduler configuration"""
        default_config = {
            "scraping": {
                "peak_hours": [9, 10, 11, 12, 13, 14, 15, 16, 17, 18],  # 9 AM - 6 PM Bhutan
                "peak_interval": 1800,      # 30 minutes during peak hours
                "normal_interval": 3600,    # 1 hour during normal hours  
                "night_interval": 7200,     # 2 hours during night
                "min_interval": 900         # Minimum 15 minutes between runs
            },
            "monitoring": {
                "enabled": True,
                "check_interval": 300,      # Check every 5 minutes
                "rss_check": True,
                "page_change_detection": True
            },
            "recovery": {
                "enabled": True,
                "daily_recovery_hour": 4,   
                "weekly_deep_recovery": 0,  #
                "max_recovery_posts": 50
            },
            "notifications": {
                "on_new_posts": True,
                "on_errors": True,
                "on_recovery": True,
                "daily_summary": True,
                "summary_hour": 19          
            }
        }
        
        config_file = "../config/scheduler_config.json"
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                return {**default_config, **config}
            except Exception as e:
                print(f" Failed to load scheduler config: {e}")
        
        # Create default config file
        with open(config_file, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        print(f"Created default scheduler config: {config_file}")
        return default_config
    
    def get_optimal_scrape_interval(self):
        """Calculate optimal scraping interval based on current time"""
        now = datetime.now()
        hour = now.hour
        
        config = self.config["scraping"]
        
        if hour in config["peak_hours"]:
            return config["peak_interval"]
        elif 22 <= hour or hour <= 6:  # Night time (10 PM - 6 AM)
            return config["night_interval"]
        else:  # Normal hours
            return config["normal_interval"]
    
    def should_run_scraper(self):
        """Determine if scraper should run based on timing and recent activity"""
        last_run_file = "data/last_run.txt"
        
        try:
            with open(last_run_file, 'r') as f:
                last_run = datetime.fromisoformat(f.read().strip())
                time_since_last = (datetime.now() - last_run).total_seconds()
                
                optimal_interval = self.get_optimal_scrape_interval()
                min_interval = self.config["scraping"]["min_interval"]
                
                # Don't run if too recent
                if time_since_last < min_interval:
                    return False, f"Too recent (last run {time_since_last:.0f}s ago, min {min_interval}s)"
                
                # Run if past optimal interval
                if time_since_last >= optimal_interval:
                    return True, f"Time for scheduled run ({time_since_last:.0f}s since last)"
                
                # Check if new content detected
                if self.post_monitor.check_kuensel_rss() or self.post_monitor.check_facebook_api_alternative():
                    return True, "New content detected"
                    
                return False, f"Waiting for optimal interval ({optimal_interval - time_since_last:.0f}s remaining)"
                
        except FileNotFoundError:
            return True, "First run"
    
    def should_run_recovery(self):
        """Determine if recovery should run"""
        if not self.config["recovery"]["enabled"]:
            return False, "Recovery disabled"
            
        now = datetime.now()
        recovery_config = self.config["recovery"]
        
        # Daily recovery check
        if now.hour == recovery_config["daily_recovery_hour"]:
            recovery_file = f"data/last_recovery_{now.date()}.txt"
            if not os.path.exists(recovery_file):
                # Mark as done for today
                with open(recovery_file, 'w') as f:
                    f.write(now.isoformat())
                return True, "Daily recovery time"
        
        # Weekly deep recovery
        if (now.weekday() == recovery_config["weekly_deep_recovery"] and 
            now.hour == recovery_config["daily_recovery_hour"]):
            weekly_file = f"data/last_weekly_recovery_{now.isocalendar()[1]}.txt"
            if not os.path.exists(weekly_file):
                with open(weekly_file, 'w') as f:
                    f.write(now.isoformat())
                return True, "Weekly deep recovery time"
        
        return False, "Not recovery time"
    
    def should_send_daily_summary(self):
        """Check if daily summary should be sent"""
        if not self.config["notifications"]["daily_summary"]:
            return False
            
        now = datetime.now()
        if now.hour == self.config["notifications"]["summary_hour"]:
            summary_file = f"data/daily_summary_{now.date()}.txt"
            if not os.path.exists(summary_file):
                with open(summary_file, 'w') as f:
                    f.write(now.isoformat())
                return True
        return False
    
    def run_scraper(self, reason="Scheduled run"):
        """Run the scraper"""
        print(f"🚀 Running scraper - {reason}")
        
        try:
            result = subprocess.run(
                ["python3", "facebook_scrapper.py"], 
                capture_output=True, 
                text=True,
                timeout=1800  # 30 minute timeout
            )
            
            if result.returncode == 0:
                print("Scraper completed successfully")
                return True
            else:
                error_msg = result.stderr or result.stdout
                print(f"Scraper failed: {error_msg}")
                if self.config["notifications"]["on_errors"]:
                    self.notifier.notify_scraper_completed(success=False, errors=error_msg)
                return False
                
        except subprocess.TimeoutExpired:
            error_msg = "Scraper timed out after 30 minutes"
            print(f"{error_msg}")
            if self.config["notifications"]["on_errors"]:
                self.notifier.notify_scraper_completed(success=False, errors=error_msg)
            return False
        except Exception as e:
            error_msg = f"Failed to run scraper: {e}"
            print(f"{error_msg}")
            if self.config["notifications"]["on_errors"]:
                self.notifier.notify_scraper_completed(success=False, errors=error_msg)
            return False
    
    def run_recovery(self, reason="Scheduled recovery"):
        """Run historical recovery"""
        print(f"Running recovery - {reason}")
        
        try:
            result = subprocess.run(
                ["python3", "historical_recovery.py"], 
                capture_output=True, 
                text=True,
                timeout=3600  # 1 hour timeout for recovery
            )
            
            if result.returncode == 0:
                print("Recovery completed successfully")
                if self.config["notifications"]["on_recovery"]:
                    # Parse output to see if posts were recovered
                    if "Recovered" in result.stdout:
                        self.notifier.notify_new_posts_detected(0)  # Recovery notification
                return True
            else:
                print(f"Recovery failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("Recovery timed out after 1 hour")
            return False
        except Exception as e:
            print(f"Failed to run recovery: {e}")
            return False
    
    def send_daily_summary(self):
        """Send daily summary"""
        print("Sending daily summary...")
        
        try:
            status = self.dashboard.get_system_status()
            posts = status.get('posts', {})
            
            subject = f"Kuensel Scraper - Daily Summary ({datetime.now().strftime('%Y-%m-%d')})"
            message = f"""
Daily Summary for Kuensel Facebook Scraper
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Statistics:
• Total Posts: {posts.get('total', 'Unknown')}
• Latest Post: {posts.get('latest_date', 'Unknown')}
• Hours Since Latest: {posts.get('hours_since_latest', 'Unknown')}

System Status:
• Scraper: {status.get('scraper', {}).get('status', 'Unknown')}
• Schedule: Active (Next run in {status.get('schedule', {}).get('minutes_until_next', '?')} minutes)
• Monitoring: {status.get('monitoring', {}).get('post_monitor', 'Unknown')}

---
Automated daily summary from Kuensel Facebook Scraper
            """
            
            self.notifier.send_email_notification(subject, message)
            self.notifier.send_webhook_notification(f"**{subject}**\n{message}")
            
        except Exception as e:
            print(f"Failed to send daily summary: {e}")
    
    def run_single_cycle(self):
        """Run a single monitoring cycle"""
        now = datetime.now()
        print(f"\n{now.strftime('%Y-%m-%d %H:%M:%S')} - Running monitoring cycle")
        
        actions_taken = []
        
        # Check if scraper should run
        should_scrape, scrape_reason = self.should_run_scraper()
        if should_scrape:
            if self.run_scraper(scrape_reason):
                actions_taken.append("Scraper")
            else:
                actions_taken.append("Scraper")
        else:
            print(f"Scraper: {scrape_reason}")
        
        # Check if recovery should run
        should_recover, recovery_reason = self.should_run_recovery()
        if should_recover:
            if self.run_recovery(recovery_reason):
                actions_taken.append("Recovery")
            else:
                actions_taken.append("Recovery")
        else:
            print(f"Recovery: {recovery_reason}")
        
        # Check if daily summary should be sent
        if self.should_send_daily_summary():
            self.send_daily_summary()
            actions_taken.append("Summary")
        
        if actions_taken:
            print(f"Actions taken: {', '.join(actions_taken)}")
        else:
            print("No actions needed this cycle")
        
        return len(actions_taken) > 0
    
    def run_continuous_monitoring(self):
        """Run continuous smart monitoring"""
        print("Starting Smart Scheduler - Continuous Monitoring")
        print("="*60)
        
        check_interval = self.config["monitoring"]["check_interval"]
        
        while True:
            try:
                self.run_single_cycle()
                
                next_check = datetime.now() + timedelta(seconds=check_interval)
                print(f"Next check at {next_check.strftime('%H:%M:%S')} (in {check_interval}s)")
                print("-" * 60)
                
                time.sleep(check_interval)
                
            except KeyboardInterrupt:
                print("\nSmart Scheduler stopped by user")
                break
            except Exception as e:
                print(f"Scheduler error: {e}")
                time.sleep(60)  # Wait a minute before retrying

def main():
    """Main scheduler function"""
    import sys
    
    scheduler = SmartScheduler()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--continuous":
            scheduler.run_continuous_monitoring()
        elif sys.argv[1] == "--once":
            scheduler.run_single_cycle()
        elif sys.argv[1] == "--dashboard":
            scheduler.dashboard.print_dashboard()
        elif sys.argv[1] == "--config":
            print("Current scheduler configuration:")
            print(json.dumps(scheduler.config, indent=2))
        else:
            print("Usage: python3 smart_scheduler.py [--continuous|--once|--dashboard|--config]")
    else:
        # Default: run once
        scheduler.run_single_cycle()

if __name__ == "__main__":
    main()
