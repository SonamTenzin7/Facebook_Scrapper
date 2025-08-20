"""
Historical Post Recovery System
Attempts to find and recover posts that might have been missed during regular scraping
"""

from facebook_scrapper import FacebookScraper
import json
from datetime import datetime, timedelta
import time

class HistoricalPostRecovery(FacebookScraper):
    def __init__(self):
        super().__init__()
        self.recovered_posts = []
        
    def deep_timeline_scrape(self, page_url="https://www.facebook.com/Kuensel", days_back=7):
        """
        Perform a deep scrape going back several days to find missed posts
        """
        print(f"Starting historical recovery for last {days_back} days...")
        
        try:
            if not self.login():
                return []
            
            # Navigate to page
            self.driver.get(page_url)
            time.sleep(3)
            
            # Try to access different sections that might have older posts
            sections_to_check = [
                ("Posts", "//a[@role='tab' and contains(text(), 'Posts')]"),
                ("Timeline", "//a[contains(text(), 'Timeline') or contains(text(), 'All')]"),
                ("Recent", "//span[contains(text(), 'Recent') or contains(text(), 'All posts')]")
            ]
            
            for section_name, xpath in sections_to_check:
                try:
                    elements = self.driver.find_elements(By.XPATH, xpath)
                    if elements:
                        print(f"📂 Checking {section_name} section...")
                        self.driver.execute_script("arguments[0].click();", elements[0])
                        time.sleep(2)
                        break
                except:
                    continue
            
            # Aggressive scrolling to load older content
            posts_found = 0
            scroll_attempts = 0
            max_scrolls = 50  # More aggressive scrolling
            
            while scroll_attempts < max_scrolls:
                print(f"Deep scroll #{scroll_attempts + 1} (Found {posts_found} posts so far)")
                
                # Expand see more links
                see_more_elements = self.driver.find_elements(
                    By.XPATH, "//div[contains(@role, 'button') and contains(text(), 'See more')]"
                )[:5]
                for element in see_more_elements:
                    try:
                        self.driver.execute_script("arguments[0].click();", element)
                        time.sleep(0.5)
                    except:
                        pass
                
                # Get posts from current view
                current_posts = self.extract_posts_from_page()
                new_posts = 0
                
                for post in current_posts:
                    if self.is_valid_post(post) and not self.is_duplicate(post):
                        # Check if post is within our date range
                        if self.is_recent_enough(post, days_back):
                            self.recovered_posts.append(post)
                            new_posts += 1
                            posts_found += 1
                
                if new_posts == 0:
                    print(f" No new posts in scroll #{scroll_attempts + 1}")
                    if scroll_attempts > 10:  # Give up after 10 empty scrolls
                        break
                
                # Scroll down more aggressively
                self.driver.execute_script("""
                    window.scrollTo(0, document.body.scrollHeight);
                    setTimeout(function() {
                        window.scrollTo(0, document.body.scrollHeight + 1000);
                    }, 1000);
                """)
                time.sleep(3)
                scroll_attempts += 1
            
            print(f"Historical recovery complete: Found {len(self.recovered_posts)} posts")
            return self.recovered_posts
            
        except Exception as e:
            print(f"Error in historical recovery: {e}")
            return []
        finally:
            self.driver.quit()
    
    def is_recent_enough(self, post, days_back):
        """Check if post is within the specified date range"""
        try:
            # This would need to be implemented based on how we can extract post dates
            # For now, assume all posts are recent enough
            return True
        except:
            return True
    
    def is_duplicate(self, post):
        """Check if post already exists in our database"""
        try:
            with open('data/kuensel_posts_master.json', 'r') as f:
                data = json.load(f)
                existing_posts = data.get('posts', [])
                
            post_content = post.get('content', '').lower()
            for existing in existing_posts:
                existing_content = existing.get('content', '').lower()
                if len(post_content) > 50 and post_content in existing_content:
                    return True
                    
            return False
        except:
            return False
    
    def save_recovered_posts(self):
        """Add recovered posts to the master file"""
        if not self.recovered_posts:
            print("No posts to recover")
            return
            
        try:
            with open('data/kuensel_posts_master.json', 'r') as f:
                data = json.load(f)
            
            # Add recovered posts
            original_count = len(data.get('posts', []))
            for post in self.recovered_posts:
                data['posts'].insert(0, post)  # Add to beginning
            
            # Update metadata
            if 'scraping_session' in data:
                data['scraping_session']['total_posts'] = len(data['posts'])
                data['scraping_session']['recovered_posts'] = len(self.recovered_posts)
                data['scraping_session']['timestamp'] = datetime.now().isoformat()
            
            # Save updated data
            with open('data/kuensel_posts_master.json', 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"Saved {len(self.recovered_posts)} recovered posts")
            print(f"Total posts: {original_count} → {len(data['posts'])}")
            
            # Regenerate static API
            import subprocess
            subprocess.run(['python3', 'generate_static_api.py'], check=True)
            print("Regenerated static API files")
            
        except Exception as e:
            print(f"Error saving recovered posts: {e}")

def run_historical_recovery():
    """Run the historical post recovery process"""
    recovery = HistoricalPostRecovery()
    
    # Run recovery for last week
    recovered = recovery.deep_timeline_scrape(days_back=7)
    
    if recovered:
        recovery.save_recovered_posts()
        print(f"Recovery complete: {len(recovered)} posts recovered")
    else:
        print(" No posts needed recovery")

if __name__ == "__main__":
    run_historical_recovery()
