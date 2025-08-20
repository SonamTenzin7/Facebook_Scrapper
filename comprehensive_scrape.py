#!/usr/bin/env python3
"""
Force scraper to find older posts by removing time restrictions and expanding search
"""

from facebook_scrapper import FacebookScraper
import json
from datetime import datetime

def force_comprehensive_scrape():
    """Force a comprehensive scrape ignoring recent limitations"""
    
    # Initialize scraper
    scraper = FacebookScraper()
    
    # Clear existing post IDs to allow re-scraping everything
    scraper.existing_post_ids = set()
    scraper.seen_post_hashes = set()
    
    print("🚀 Starting comprehensive scrape with no restrictions...")
    
    try:
        # Force scrape with higher limits
        posts = scraper.scrape_posts(
            page_url="https://www.facebook.com/Kuensel",
            target_count=50,  # Higher target
            max_scrolls=20    # More scrolls
        )
        
        if posts:
            print(f"📊 Found {len(posts)} total posts")
            
            # Search for nursing post in results
            nursing_posts = []
            for post in posts:
                content = post.get('content', '').lower()
                title = post.get('title', '').lower()
                
                if any(keyword in content or keyword in title for keyword in [
                    'nursing', 'science student', 'neten dorji', 'apollo bhutan', 
                    'arura nursing', 'competitive result', 'gnm programme'
                ]):
                    nursing_posts.append(post)
                    print(f"🎯 Found nursing-related post: {post.get('title', 'No title')[:100]}...")
            
            if nursing_posts:
                print(f"✅ Found {len(nursing_posts)} nursing-related posts!")
                # Save them
                with open('nursing_posts_found.json', 'w') as f:
                    json.dump(nursing_posts, f, indent=2)
                print("💾 Saved to nursing_posts_found.json")
            else:
                print("❌ No nursing posts found in comprehensive scrape")
                
            # Save all posts for manual inspection
            with open('comprehensive_scrape_results.json', 'w') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'total_posts': len(posts),
                    'posts': posts
                }, f, indent=2)
            print(f"💾 All {len(posts)} posts saved to comprehensive_scrape_results.json")
            
        else:
            print("❌ No posts found in comprehensive scrape")
            
    except Exception as e:
        print(f"❌ Error during comprehensive scrape: {e}")
        import traceback
        traceback.print_exc()
    finally:
        scraper.driver.quit()

if __name__ == "__main__":
    force_comprehensive_scrape()
