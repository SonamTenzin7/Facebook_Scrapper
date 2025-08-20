"""
Post Monitoring System
Monitors for new posts using multiple sources and triggers scraper when needed
"""

import requests
import json
import time
from datetime import datetime
import hashlib
import os

class PostMonitor:
    def __init__(self):
        self.known_post_hashes = set()
        self.load_known_posts()
    
    def load_known_posts(self):
        """Load existing post hashes to detect new posts"""
        try:
            with open('data/kuensel_posts_master.json', 'r') as f:
                data = json.load(f)
                
            for post in data.get('posts', []):
                content = post.get('content', '')
                if content:
                    post_hash = hashlib.md5(content.encode()).hexdigest()[:16]
                    self.known_post_hashes.add(post_hash)
                    
            print(f"📚 Loaded {len(self.known_post_hashes)} known post signatures")
        except Exception as e:
            print(f"⚠️  Could not load known posts: {e}")
    
    def check_kuensel_rss(self):
        """Check Kuensel's RSS feed for new posts (if available)"""
        rss_urls = [
            "https://kuenselonline.com/feed/",
            "https://kuenselonline.com/rss.xml",
            "https://www.kuenselonline.com/feed/"
        ]
        
        new_posts_detected = False
        
        for rss_url in rss_urls:
            try:
                print(f"🔍 Checking RSS feed: {rss_url}")
                response = requests.get(rss_url, timeout=10)
                
                if response.status_code == 200:
                    # Simple RSS parsing (would need proper XML parsing for production)
                    content = response.text
                    
                    # Look for new content patterns
                    if self.detect_new_content_patterns(content):
                        print(f"✅ New content detected in RSS feed")
                        new_posts_detected = True
                        break
                        
            except Exception as e:
                print(f"⚠️  RSS check failed for {rss_url}: {e}")
                continue
        
        return new_posts_detected
    
    def detect_new_content_patterns(self, content):
        """Detect if RSS content contains new posts"""
        # This would need more sophisticated parsing in production
        # For now, just check if there are recent timestamps
        current_date = datetime.now().strftime("%Y-%m-%d")
        return current_date in content
    
    def check_facebook_api_alternative(self):
        """Check alternative Facebook data sources"""
        # Since Facebook API is restricted, we could check:
        # 1. Facebook's public page source for changes
        # 2. Third-party social media monitoring services
        # 3. IFTTT or Zapier triggers (if configured)
        
        try:
            # Simple approach: Check if Facebook page has changed
            response = requests.get("https://www.facebook.com/Kuensel", timeout=10)
            if response.status_code == 200:
                page_hash = hashlib.md5(response.text.encode()).hexdigest()
                
                # Compare with stored hash
                hash_file = "data/last_page_hash.txt"
                if os.path.exists(hash_file):
                    with open(hash_file, 'r') as f:
                        last_hash = f.read().strip()
                    
                    if page_hash != last_hash:
                        print("✅ Facebook page content changed - new posts likely")
                        with open(hash_file, 'w') as f:
                            f.write(page_hash)
                        return True
                else:
                    # First run, store hash
                    with open(hash_file, 'w') as f:
                        f.write(page_hash)
                    
        except Exception as e:
            print(f"⚠️  Facebook page check failed: {e}")
            
        return False
    
    def trigger_scraper_if_needed(self):
        """Trigger the scraper if new posts are detected"""
        new_content = False
        
        # Check multiple sources
        if self.check_kuensel_rss():
            new_content = True
        
        if self.check_facebook_api_alternative():
            new_content = True
        
        if new_content:
            print("🚀 New content detected - triggering scraper...")
            try:
                os.system("python3 facebook_scrapper.py")
                print("✅ Scraper triggered successfully")
            except Exception as e:
                print(f"❌ Failed to trigger scraper: {e}")
        else:
            print("ℹ️  No new content detected")
    
    def continuous_monitoring(self, check_interval=300):
        """Run continuous monitoring every N seconds"""
        print(f"🔄 Starting continuous monitoring (checking every {check_interval} seconds)")
        
        while True:
            try:
                print(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Checking for new posts...")
                self.trigger_scraper_if_needed()
                print(f"😴 Sleeping for {check_interval} seconds...")
                time.sleep(check_interval)
                
            except KeyboardInterrupt:
                print("\n⏹️  Monitoring stopped by user")
                break
            except Exception as e:
                print(f"❌ Monitor error: {e}")
                time.sleep(60)  # Wait a minute before retrying

def run_post_monitoring():
    """Run the post monitoring system"""
    monitor = PostMonitor()
    
    # Check once
    monitor.trigger_scraper_if_needed()

def run_continuous_monitoring():
    """Run continuous post monitoring"""
    monitor = PostMonitor()
    monitor.continuous_monitoring(check_interval=300)  # Check every 5 minutes

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--continuous":
        run_continuous_monitoring()
    else:
        run_post_monitoring()
