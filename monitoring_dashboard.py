"""
Comprehensive Monitoring Dashboard
Integrates all timing solutions and provides real-time status
"""

import json
import time
import os
from datetime import datetime, timedelta
from post_monitor import PostMonitor
from notification_system import NotificationSystem
from historical_recovery import HistoricalPostRecovery
import subprocess

class MonitoringDashboard:
    def __init__(self):
        self.post_monitor = PostMonitor()
        self.notifier = NotificationSystem()
        self.last_check_times = {}
        self.system_stats = {}
        
    def get_system_status(self):
        """Get comprehensive system status"""
        status = {
            "timestamp": datetime.now().isoformat(),
            "scraper": self.get_scraper_status(),
            "posts": self.get_posts_status(),
            "schedule": self.get_schedule_status(),
            "github_actions": self.get_github_actions_status(),
            "monitoring": self.get_monitoring_status()
        }
        return status
    
    def get_scraper_status(self):
        """Get scraper status"""
        try:
            # Check if scraper is currently running
            result = subprocess.run(
                ["ps", "aux"], 
                capture_output=True, 
                text=True
            )
            is_running = "facebook_scrapper.py" in result.stdout
            
            # Check last run time
            log_file = "log/scrapper.log"
            last_run = None
            if os.path.exists(log_file):
                try:
                    with open(log_file, 'r') as f:
                        lines = f.readlines()
                        if lines:
                            # Parse last log entry for timestamp
                            for line in reversed(lines[-10:]):  # Check last 10 lines
                                if "Starting" in line or "Completed" in line:
                                    # Extract timestamp from log
                                    last_run = line.split()[0] + " " + line.split()[1]
                                    break
                except Exception:
                    pass
            
            return {
                "running": is_running,
                "last_run": last_run,
                "status": "running" if is_running else "idle"
            }
        except Exception as e:
            return {"error": str(e), "status": "unknown"}
    
    def get_posts_status(self):
        """Get posts database status"""
        try:
            with open('data/kuensel_posts_master.json', 'r') as f:
                data = json.load(f)
            
            posts = data.get('posts', [])
            if not posts:
                return {"total": 0, "error": "No posts found"}
            
            # Get latest post date
            latest_date = None
            for post in posts:
                if post.get('date'):
                    try:
                        post_date = datetime.strptime(post['date'], '%Y-%m-%d')
                        if not latest_date or post_date > latest_date:
                            latest_date = post_date
                    except Exception:
                        continue
            
            # Calculate freshness
            hours_since_latest = None
            if latest_date:
                hours_since_latest = (datetime.now() - latest_date).total_seconds() / 3600
            
            return {
                "total": len(posts),
                "latest_date": latest_date.isoformat() if latest_date else None,
                "hours_since_latest": round(hours_since_latest, 1) if hours_since_latest else None,
                "freshness": "fresh" if hours_since_latest and hours_since_latest < 24 else "stale"
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_schedule_status(self):
        """Get GitHub Actions schedule status"""
        try:
            # Calculate next run times based on cron schedules
            now = datetime.now()
            
            # Main schedule: 5,35 * * * * (every 30 minutes at :05 and :35)
            next_main = now.replace(minute=5 if now.minute < 5 else (35 if now.minute < 35 else 5), second=0, microsecond=0)
            if next_main <= now:
                next_main += timedelta(hours=1 if now.minute >= 35 else 0)
                if now.minute >= 35:
                    next_main = next_main.replace(minute=5)
            
            # Peak hours: 15,45 3-12 * * * (business hours, additional runs)
            next_peak = None
            if 3 <= now.hour <= 12:  # During business hours
                next_peak = now.replace(minute=15 if now.minute < 15 else (45 if now.minute < 45 else 15), second=0, microsecond=0)
                if next_peak <= now:
                    next_peak += timedelta(hours=1 if now.minute >= 45 else 0)
                    if now.minute >= 45:
                        next_peak = next_peak.replace(minute=15)
                    if next_peak.hour > 12:
                        next_peak = now.replace(hour=3, minute=15, second=0, microsecond=0) + timedelta(days=1)
            else:
                next_peak = now.replace(hour=3, minute=15, second=0, microsecond=0)
                if next_peak <= now:
                    next_peak += timedelta(days=1)
            
            return {
                "next_main_run": next_main.isoformat(),
                "next_peak_run": next_peak.isoformat() if next_peak else None,
                "minutes_until_next": round((min(next_main, next_peak or next_main) - now).total_seconds() / 60, 1)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_github_actions_status(self):
        """Get GitHub Actions status"""
        # This would require GitHub API integration
        # For now, return placeholder
        return {
            "status": "enabled",
            "last_workflow_run": "unknown",
            "note": "Requires GitHub API integration for real-time status"
        }
    
    def get_monitoring_status(self):
        """Get monitoring system status"""
        return {
            "post_monitor": "active",
            "notifications": "configured" if self.notifier.config.get("email", {}).get("enabled") else "disabled",
            "historical_recovery": "available",
            "adaptive_timing": "enabled"
        }
    
    def print_dashboard(self):
        """Print a beautiful dashboard"""
        status = self.get_system_status()
        
        print("\n" + "="*80)
        print("📊 KUENSEL FACEBOOK SCRAPER - MONITORING DASHBOARD")
        print("="*80)
        print(f"🕐 Last Updated: {status['timestamp']}")
        print()
        
        # Scraper Status
        scraper = status['scraper']
        scraper_icon = "🟢" if scraper.get('status') == 'running' else "🔵"
        print(f"{scraper_icon} SCRAPER STATUS: {scraper.get('status', 'unknown').upper()}")
        if scraper.get('last_run'):
            print(f"   ⏰ Last Run: {scraper['last_run']}")
        print()
        
        # Posts Status
        posts = status['posts']
        if 'error' not in posts:
            freshness_icon = "🟢" if posts.get('freshness') == 'fresh' else "🟡"
            print(f"{freshness_icon} POSTS DATABASE: {posts['total']} posts")
            if posts.get('latest_date'):
                print(f"   📅 Latest Post: {posts['latest_date']}")
                if posts.get('hours_since_latest'):
                    print(f"   ⏳ Hours Since Latest: {posts['hours_since_latest']}")
        else:
            print(f"🔴 POSTS DATABASE: {posts['error']}")
        print()
        
        # Schedule Status
        schedule = status['schedule']
        if 'error' not in schedule:
            print(f"🟢 SCHEDULE STATUS: Active")
            print(f"   ⏰ Next Main Run: {schedule['next_main_run']}")
            if schedule.get('next_peak_run'):
                print(f"   ⚡ Next Peak Run: {schedule['next_peak_run']}")
            print(f"   ⏱️  Minutes Until Next: {schedule['minutes_until_next']}")
        else:
            print(f"🔴 SCHEDULE STATUS: {schedule['error']}")
        print()
        
        # Monitoring Status
        monitoring = status['monitoring']
        print(f"🟢 MONITORING SYSTEMS:")
        print(f"   📡 Post Monitor: {monitoring['post_monitor']}")
        print(f"   🔔 Notifications: {monitoring['notifications']}")
        print(f"   🏛️  Historical Recovery: {monitoring['historical_recovery']}")
        print(f"   ⚡ Adaptive Timing: {monitoring['adaptive_timing']}")
        print()
        
        print("="*80)
        print("💡 TIPS:")
        print("   • Run with --monitor for continuous monitoring")
        print("   • Run with --recover for historical post recovery")
        print("   • Run with --test-notifications to test alerts")
        print("="*80)
    
    def continuous_monitoring(self, interval=300):
        """Run continuous monitoring with dashboard updates"""
        print("🔄 Starting continuous monitoring dashboard...")
        
        while True:
            try:
                os.system('clear')  # Clear screen for fresh dashboard
                self.print_dashboard()
                
                # Check for new posts
                print(f"\n🔍 Checking for new posts...")
                self.post_monitor.trigger_scraper_if_needed()
                
                print(f"\n😴 Next update in {interval} seconds...")
                print("   Press Ctrl+C to stop monitoring")
                
                time.sleep(interval)
                
            except KeyboardInterrupt:
                print("\n⏹️  Monitoring stopped by user")
                break
            except Exception as e:
                print(f"❌ Dashboard error: {e}")
                time.sleep(60)
    
    def run_recovery_check(self):
        """Run historical recovery check"""
        print("🏛️  Running historical post recovery...")
        try:
            recovery = HistoricalPostRecovery()
            recovered_posts = recovery.run_recovery()
            
            if recovered_posts:
                print(f"✅ Recovered {len(recovered_posts)} posts")
                self.notifier.notify_new_posts_detected(len(recovered_posts))
            else:
                print("ℹ️  No new posts recovered")
                
        except Exception as e:
            print(f"❌ Recovery failed: {e}")

def main():
    """Main dashboard function"""
    import sys
    
    dashboard = MonitoringDashboard()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--monitor":
            dashboard.continuous_monitoring()
        elif sys.argv[1] == "--recover":
            dashboard.run_recovery_check()
        elif sys.argv[1] == "--test-notifications":
            dashboard.notifier.test_notifications()
        else:
            print("Usage: python3 monitoring_dashboard.py [--monitor|--recover|--test-notifications]")
    else:
        dashboard.print_dashboard()

if __name__ == "__main__":
    main()
