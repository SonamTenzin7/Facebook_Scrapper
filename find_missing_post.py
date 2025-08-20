#!/usr/bin/env python3
"""
Debug script to find the missing "Non-science students show competitive results in nursing" post
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import json
from facebook_scrapper import FacebookScraper

def debug_find_nursing_post():
    """Search for the specific nursing post with detailed logging"""
    
    # Initialize scraper but with less restrictive validation
    scraper = FacebookScraper()
    
    try:
        # Navigate to page
        print("🔍 Searching for nursing post...")
        scraper.driver.get("https://www.facebook.com/Kuensel")
        time.sleep(3)
        
        # Scroll through multiple sections to find the post
        for scroll_num in range(1, 8):
            print(f"\n📜 Scroll #{scroll_num}")
            
            # Expand 'See more' links
            see_more_elements = scraper.driver.find_elements(
                By.XPATH, "//div[contains(@role, 'button') and contains(text(), 'See more')]"
            )
            for element in see_more_elements[:2]:  # Limit to avoid too many clicks
                try:
                    scraper.driver.execute_script("arguments[0].click();", element)
                    time.sleep(1)
                except:
                    pass
            
            # Get page source and parse
            page_source = scraper.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Look for post containers
            post_elements = soup.find_all('div', attrs={'data-pagelet': 'FeedUnit'})
            if not post_elements:
                post_elements = soup.find_all('div', {'role': 'article'})
            if not post_elements:
                post_elements = soup.find_all('div', class_=lambda x: x and any(
                    keyword in x for keyword in ['userContentWrapper', 'story_body_container', '_1dwg']
                ))
            
            print(f"Found {len(post_elements)} potential post elements")
            
            # Search each post for nursing content
            for i, post_elem in enumerate(post_elements[:15]):  # Limit to avoid spam
                text_content = post_elem.get_text().lower()
                
                # Check for nursing-related keywords
                nursing_keywords = ['nursing', 'science student', 'competitive result', 'neten dorji', 
                                  'apollo bhutan', 'arura nursing', 'gnm programme']
                
                matches = [keyword for keyword in nursing_keywords if keyword in text_content]
                
                if matches:
                    print(f"\n🎯 POTENTIAL MATCH in post #{i}:")
                    print(f"   Keywords found: {matches}")
                    print(f"   Content preview: {text_content[:200]}...")
                    
                    # Try to extract full post data
                    try:
                        post_data = scraper.extract_post_data(post_elem, i)
                        if post_data:
                            print(f"   Title: {post_data.get('title', 'No title')[:100]}...")
                            print(f"   Content length: {len(post_data.get('content', ''))}")
                            print(f"   Valid post: {scraper.is_valid_post(post_data)}")
                            
                            # Check what validation fails
                            content = post_data.get('content', '')
                            if len(content.strip()) < 10:
                                print(f"   ❌ Failed: Content too short ({len(content.strip())} chars)")
                            elif len(content.strip()) < 25 and not post_data.get('attachment', {}).get('images'):
                                print(f"   ❌ Failed: Short content without media ({len(content.strip())} chars)")
                            else:
                                print(f"   ✅ Should pass validation")
                                
                                # Save this post for inspection
                                with open('found_nursing_post.json', 'w') as f:
                                    json.dump(post_data, f, indent=2)
                                print(f"   💾 Saved to found_nursing_post.json")
                    except Exception as e:
                        print(f"   ❌ Error extracting post data: {e}")
                
                elif any(word in text_content for word in ['non-science', 'non science', 'student', 'nursing']):
                    print(f"   Partial match in post #{i}: {text_content[:100]}...")
            
            # Scroll down
            scraper.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
        print(f"\n✅ Search complete")
        
    except Exception as e:
        print(f"❌ Error during search: {e}")
    finally:
        scraper.driver.quit()

if __name__ == "__main__":
    debug_find_nursing_post()
