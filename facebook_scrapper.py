from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import json
import hashlib
from datetime import datetime
import html
import re
import os
import requests
from urllib.parse import urljoin, urlparse

class FacebookScraper:
    def __init__(self, config_file="config.json"):
        self.config = self.load_config(config_file)
        self.driver = None
        self.posts_data = []
        self.seen_post_hashes = set()
        self.setup_driver()

    def load_config(self, config_file):
        """Load configuration from Json file"""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Config File {config_file} not found. Using default configuration.")
           
            return {
                "credentials": {"email": "", "password": ""},
                "scraping": {"headless": True, "max_scrolls": 15, "scroll_pause": 3, "target_count": 25},
                "output": {"folder": "data/", "filename_prefix": "kuensel_posts"},
                "download_images": False
            }

    def setup_driver(self):
        """Setup Chrome driver with appropriate options"""
        chrome_options = Options()
        if self.config["scraping"]["headless"]:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

        self.driver = webdriver.Chrome(options=chrome_options)
        print("WebDriver initialized successfully")

    def login(self):
        """Login to Facebook"""
        try:
            # Read credentials from config file 
            email = self.config["credentials"]["email"]
            password = self.config["credentials"]["password"]

            if not email or not password:
                print("Email and password not configured in config.json")
                return False

            self.driver.get("https://www.facebook.com/login")

            # Fill email
            email_field = self.driver.find_element(By.ID, "email")
            email_field.send_keys(email)

            # Fill password
            password_field = self.driver.find_element(By.ID, "pass")
            password_field.send_keys(password)
            # Click login
            login_button = self.driver.find_element(By.NAME, "login")
            login_button.click()

            # Waiting for login to complete
            time.sleep(5)

            print("Login successful")
            return True

        except Exception as e:
            print(f"Login failed: {e}")
            return False

    def navigate_to_page(self, page_url): 
        """Navigate to the target Facebook page"""
        try:
            self.driver.get(page_url)
            time.sleep(3)
            print(f"Navigated to: {page_url}")
            return True
        except Exception as e:
            print(f"Failed to navigate to page: {e}")
            return False

    def scroll_page(self, scroll_pause_time=None):
        """Scroll down the page to load more content"""
        if scroll_pause_time is None:
            scroll_pause_time = self.config["scraping"]["scroll_pause"]

        # Scrolling down
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait for new content to load
        time.sleep(scroll_pause_time)

        return True

    def expand_see_more_links(self):
        """Expand all 'See more' links to get full content"""
        try:
            # Common selectors for "See more" links
            see_more_selectors = [
                "[role='button'][tabindex='0']",  # Generic clickable elements
                "div[role='button']:has-text('See more')",
                "span[role='button']:has-text('See more')",
                "[aria-label*='See more']",
                "div[tabindex='0']:has-text('See more')",
                "span:has-text('See more')",
                "div:has-text('See more')"
            ]
            
            expanded_count = 0
            
            # Find and click all "See more" elements using Selenium
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
            
            # Look for elements containing "See more" text
            try:
                see_more_elements = self.driver.find_elements(By.XPATH, 
                    "//div[contains(text(), 'See more')] | //span[contains(text(), 'See more')] | //*[@aria-label[contains(., 'See more')]]")
                
                print(f"Found {len(see_more_elements)} 'See more' elements")
                
                for element in see_more_elements:
                    try:
                        # Scroll element into view
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                        time.sleep(0.5)
                        
                        # Try to click the element
                        if element.is_displayed() and element.is_enabled():
                            element.click()
                            expanded_count += 1
                            time.sleep(1)  # Wait for content to expand
                            print(f"Expanded content #{expanded_count}")
                    except (ElementClickInterceptedException, Exception) as e:
                        # Try JavaScript click as fallback
                        try:
                            self.driver.execute_script("arguments[0].click();", element)
                            expanded_count += 1
                            time.sleep(1)
                            print(f"Expanded content #{expanded_count} (JS click)")
                        except Exception as js_e:
                            print(f"Could not click 'See more' element: {js_e}")
                            continue
                            
            except Exception as e:
                print(f"Error finding 'See more' elements: {e}")
            
            print(f"Successfully expanded {expanded_count} 'See more' links")
            return expanded_count
            
        except Exception as e:
            print(f"Error in expand_see_more_links: {e}")
            return 0

    def get_page_html(self):
        """Get current page HTML"""
        return self.driver.page_source

    def extract_posts_with_beautifulsoup(self, html_content):
        """Extract posts using BeautifulSoup"""
        soup = BeautifulSoup(html_content, 'html.parser')
        posts = []

        # More comprehensive selectors for Facebook posts
        selectors = [
            "[role='article']",
            "[data-pagelet*='FeedUnit']",
            ".userContentWrapper",
            "[data-testid='fb-ufi-mention-bling-bar']",
            "div[data-ft*='top_level_post_id']",
            "div[data-ad-preview='message']",
            ".x1yztbdb",
            "[data-pagelet='Feed'] div:not([class]) > div"
        ]

        post_elements = []
        for selector in selectors:
            elements = soup.select(selector)
            post_elements.extend(elements)

        print(f"Found {len(post_elements)} potential post elements")

        # Remove duplicates while preserving order
        seen_elements = set()
        unique_elements = []
        for element in post_elements:
            element_str = str(element)[:300]  
            if element_str not in seen_elements:
                seen_elements.add(element_str)
                unique_elements.append(element)

        print(f"Found {len(unique_elements)} unique elements after deduplication")

        for i, post_element in enumerate(unique_elements):
            try:
                post_data = self.parse_single_post(post_element, i)
                if post_data:
                    posts.append(post_data)
                else:
                    print(f"Failed to parse post element {i}")
            except Exception as e:
                print(f"Error parsing post element {i}: {e}")
                continue

        print(f"Successfully parsed {len(posts)} posts")
        return posts

    def parse_single_post(self, post_element, index=0):
        """Parse individual post data with proper field extraction"""
        try:
            # Extract content 
            content = ""

            # content selectors (most common)
            content_selectors = [
                "[data-ad-preview='message']",
                ".userContent",
                "[data-testid='post_message']",
                "div[data-gt*='content']",
                "div[direction='auto']",
                "div[dir='auto']",
                "span[dir='auto']",
                "div > span:not([class])",
                "div > div > span"
            ]

            for selector in content_selectors:
                content_elem = post_element.select_one(selector)
                if content_elem:
                    temp_content = content_elem.get_text(strip=True, separator=' ')
                    if len(temp_content) > len(content) and len(temp_content) > 3:
                        content = temp_content

            # Extract timestamp
            timestamp = ""
            time_elem = post_element.find('time')
            if time_elem:
                timestamp = time_elem.get('datetime', '') or time_elem.get_text(strip=True)

            # Author information
            author = "Kuensel"  # Default for page posts
            author_id = "kuensel"  # Default page ID

            # Extract actual author if it's not a page post
            author_selectors = [
                "[data-testid='story-subtitle']",
                "[data-testid='story-footer']",
                "h3 a",
                ".fcg a"
            ]

            for selector in author_selectors:
                author_elem = post_element.select_one(selector)
                if author_elem:
                    author_text = author_elem.get_text(strip=True)
                    if author_text and author_text not in ["Kuensel", ""]:
                        author = author_text
                        break

            # Extract engagement
            reactions = 0
            comments = 0
            shares = 0

            # Look for engagement numbers in text
            all_text = post_element.get_text()
            reaction_match = re.search(r'(\d+(?:\.\d+)?[KM]?)\s*(?:like|react)', all_text, re.IGNORECASE)
            if reaction_match:
                reactions = self.parse_count(reaction_match.group(1))

            comment_match = re.search(r'(\d+(?:\.\d+)?[KM]?)\s*comment', all_text, re.IGNORECASE)
            if comment_match:
                comments = self.parse_count(comment_match.group(1))

            share_match = re.search(r'(\d+(?:\.\d+)?[KM]?)\s*share', all_text, re.IGNORECASE)
            if share_match:
                shares = self.parse_count(share_match.group(1))

            # Extract links from the post
            links = self.extract_links_from_post(post_element)

            # Extract media
            media = self.extract_media_from_post(post_element)

            # Extract additional images from Facebook photo links
            photo_images = self.extract_images_from_facebook_photo_links(links)
            if photo_images:
                print(f"Found {len(photo_images)} additional images from photo links")
                # Add to existing media images, avoiding duplicates
                for img_url in photo_images:
                    if img_url not in media["images"]:
                        media["images"].append(img_url)

            # Fetch full article content if Kuensel links are found
            article_content, article_title = self.fetch_full_article_content(links)

            # Create proper title, description, and content
            clean_content = self.clean_text(content)

            # Use article content if available, otherwise use Facebook post content
            if article_content and len(article_content) > len(clean_content):
                final_content = article_content
                print(f"Using full article content ({len(article_content)} chars)")
            else:
                final_content = clean_content
                print(f"Using Facebook post content ({len(clean_content)} chars)")

            # For title, use article title if available, otherwise extract from content
            if article_title and len(article_title) > 10:
                title = article_title
                print(f"Using article title: {title[:50]}...")
            else:
                title = self.extract_title_from_content(final_content)

            # For description, use first paragraph or next 9000 characters
            description = self.extract_description_from_content(final_content, title)

            # Category based on content analysis
            category_id = self.determine_category(final_content)

            post_data = {
                "id": hashlib.md5((final_content + str(timestamp)).encode()).hexdigest()[:16] if final_content else f"post_{index}",
                "title": title,
                "description": description,
                "content": final_content,
                "categoryID": category_id,
                "authorId": author_id,
                "authorName": author,
                "attachment": {
                    "images": media["images"],
                    "videos": media["videos"],
                    "links": links
                },
                "createdAt": datetime.now().isoformat(),
                "publishAt": timestamp if timestamp else datetime.now().isoformat(),
                "raw_content_length": len(final_content),
                "article_source": "full_article" if article_content else "facebook_post"
            }

            return post_data
        except Exception as e:
            print(f"Error in parse_single_post for index {index}: {e}")
            return None

    def extract_title_from_content(self, content):
        """Extract title from content"""
        if not content:
            return "Untitled Post"

        # Try to get first sentence
        sentences = re.split(r'[.!?]+', content)
        if sentences and len(sentences[0].strip()) > 10:
            title = sentences[0].strip()
        else:
            # Use first 100 characters
            title = content[:100].strip()

        # If title is too short, use the full content (up to 150 chars)
        if len(title) < 10:
            title = content[:150].strip() if content else "Untitled Post"

        # Ensure title ends properly
        if len(title) > 100:
            title = title[:97] + "..."

        return title

    def extract_description_from_content(self, content, title):
        """Extract description from content"""
        if not content:
            return ""

        # Remove the title from content if it's at the beginning
        if content.startswith(title):
            remaining_content = content[len(title):].strip()
        else:
            remaining_content = content

        # Get first paragraph or next 9000 characters
        paragraphs = [p.strip() for p in remaining_content.split('\n') if p.strip()]
        if paragraphs:
            description = paragraphs[0]
        else:
            description = remaining_content[:9000].strip()

        # Limit description length to 9000 characters
        if len(description) > 9000:
            description = description[:8997] + "..."

        return description

    def determine_category(self, content):
        """Determine category based on content"""
        if not content:
            return "general"

        content_lower = content.lower()

        categories = {
            "news": ["breaking", "news", "update", "latest", "report"],
            "event": ["event", "festival", "celebration", "observe", "foundation day", "ceremony"],
            "culture": ["tradition", "culture", "heritage", "festival", "dzong", "sacred"],
            "politics": ["minister", "government", "policy", "election", "parliament"],
            "sports": ["match", "game", "tournament", "score", "team", "player"],
            "advertisement": ["available", "shop", "buy", "offer", "discount", "for sale","vacancy", "job", "recruitment"],
        }

        for category, keywords in categories.items():
            if any(keyword in content_lower for keyword in keywords):
                return category

        return "general"

    def extract_links_from_post(self, post_element):
        """Extract all links from a post"""
        links = []
        photo_links = []
        
        try:
            link_elements = post_element.find_all('a', href=True)
            base_url = "https://www.facebook.com"

            for link in link_elements:
                href = link.get('href', '')
                if href:
                    if href.startswith('/'):
                        href = urljoin(base_url, href)

                    # Collect Facebook photo links separately 
                    if '/photo?' in href or '/photos/' in href or 'fbid=' in href:
                        if href not in photo_links:
                            photo_links.append(href)
                            print(f"Found Facebook photo link: {href}")
                    
                    # Filter out Facebook internal links for regular links
                    elif self.is_external_link(href) or '/permalink.php' in href:
                        if href not in links:
                            links.append(href)
                            
        except Exception as e:
            print(f"Error extracting links: {e}")

        # Store photo links in the links array with a special marker
        all_links = links + photo_links
        return all_links

    def is_external_link(self, url):
        """Check if URL is external (not Facebook internal)"""
        if not url:
            return False

        # Facebook internal URLs to exclude
        internal_patterns = [
            'facebook.com',
            '/permalink.php',
            '/photos/',
            '/photo.php',
            '/videos/',
            'fbcdn.net'
        ]

        return url.startswith('http') and not any(pattern in url for pattern in internal_patterns[:3])

    def extract_media_from_post(self, post_element):
        """Extract all media (images, videos) from a post element"""
        media = {"images": [], "videos": []}

        try:
            # Method 1: Extract images from img tags
            img_elements = post_element.find_all('img')
            for img in img_elements:
                src = img.get('src', '')
                if src and self.is_valid_image_url(src):
                    # Avoid profile pictures and emojis
                    alt = img.get('alt', '').lower()
                    if not any(keyword in alt for keyword in ['profile', 'avatar', 'emoji', 'like', 'icon']):
                        if src not in media["images"]:
                            media["images"].append(src)

            # Method 2: Extract from data attributes (multiple variants)
            data_attrs = [
                'data-imgurl', 'data-src', 'data-original', 'data-lazy-src',
                'data-img-src', 'data-background-image', 'data-image-url'
            ]
            
            for attr in data_attrs:
                elements_with_data = post_element.find_all(attrs={attr: True})
                for elem in elements_with_data:
                    img_url = elem.get(attr, '')
                    if self.is_valid_image_url(img_url) and img_url not in media["images"]:
                        media["images"].append(img_url)

            # Method 3: Extract image URLs from style attributes
            style_elements = post_element.find_all(attrs={'style': True})
            for elem in style_elements:
                style = elem.get('style', '')
                # Look for background-image URLs
                bg_image_matches = re.findall(r'background-image:\s*url\(["\']?(.*?)["\']?\)', style)
                for url in bg_image_matches:
                    if self.is_valid_image_url(url) and url not in media["images"]:
                        media["images"].append(url)

            # Method 4: Extract from srcset attributes (responsive images)
            srcset_elements = post_element.find_all(attrs={'srcset': True})
            for elem in srcset_elements:
                srcset = elem.get('srcset', '')
                # Parse srcset format: "url1 1x, url2 2x" or "url1 100w, url2 200w"
                urls = re.findall(r'(https?://[^\s,]+)', srcset)
                for url in urls:
                    if self.is_valid_image_url(url) and url not in media["images"]:
                        media["images"].append(url)

            # Method 5: Look for specific Facebook image classes/patterns
            fb_image_selectors = [
                'img[class*="scaledImageFitWidth"]',
                'img[class*="scaledImageFitHeight"]', 
                'img[class*="_46-i"]',
                'img[class*="fb_feed_image"]',
                'div[style*="background-image"]',
                'a[href*="/photo/"]',
                '[data-testid="photo"]'
            ]
            
            for selector in fb_image_selectors:
                try:
                    elements = post_element.select(selector)
                    for elem in elements:
                        # For img tags
                        if elem.name == 'img':
                            src = elem.get('src', '')
                            if src and self.is_valid_image_url(src) and src not in media["images"]:
                                media["images"].append(src)
                        # For div with background-image
                        elif elem.name == 'div':
                            style = elem.get('style', '')
                            bg_matches = re.findall(r'background-image:\s*url\(["\']?(.*?)["\']?\)', style)
                            for url in bg_matches:
                                if self.is_valid_image_url(url) and url not in media["images"]:
                                    media["images"].append(url)
                        # For links to photos
                        elif elem.name == 'a':
                            href = elem.get('href', '')
                            # Extract image URL from Facebook photo links
                            if '/photo/' in href:
                                # Look for image inside the link
                                img_in_link = elem.find('img')
                                if img_in_link:
                                    src = img_in_link.get('src', '')
                                    if src and self.is_valid_image_url(src) and src not in media["images"]:
                                        media["images"].append(src)
                except Exception as e:
                    print(f"Error with selector {selector}: {e}")

            # Method 6: Extract videos
            video_elements = post_element.find_all('video')
            for video in video_elements:
                src = video.get('src', '')
                if src and src not in media["videos"]:
                    media["videos"].append(src)
                    
            # Also check for video data attributes
            video_data_elements = post_element.find_all(attrs={"data-video-url": True})
            for elem in video_data_elements:
                video_url = elem.get('data-video-url', '')
                if video_url and video_url not in media["videos"]:
                    media["videos"].append(video_url)

            print(f"Extracted {len(media['images'])} images, {len(media['videos'])} videos")

        except Exception as e:
            print(f"Error extracting media: {e}")

        return media

    def extract_images_from_facebook_photo_links(self, links):
        """Extract actual image URLs from Facebook photo links"""
        image_urls = []
        
        try:
            for link in links:
                if '/photo?' in link or 'fbid=' in link:
                    print(f"Processing Facebook photo link: {link}")
                    
                    try:
                        # Navigate to the photo page
                        self.driver.execute_script(f"window.open('{link}', '_blank');")
                        self.driver.switch_to.window(self.driver.window_handles[-1])
                        time.sleep(3)  # Wait for page to load
                        
                        # Get page source and parse with BeautifulSoup
                        photo_page_html = self.driver.page_source
                        soup = BeautifulSoup(photo_page_html, 'html.parser')
                        
                        # Look for the main photo image with multiple selectors
                        photo_selectors = [
                            'img[data-pagelet="MediaViewerPhoto"]',
                            'img[class*="spotlight"]',
                            'img[style*="max-height"]',
                            'img[src*="fbcdn.net"][src*="scontent"]',
                            '.spotlight img',
                            '[data-testid="photo-viewer"] img',
                            '.photoContainer img',
                            'img[class*="scaledImageFit"]'
                        ]
                        
                        found_image = False
                        for selector in photo_selectors:
                            try:
                                img_elements = soup.select(selector)
                                for img in img_elements:
                                    src = img.get('src', '')
                                    if src and self.is_valid_image_url(src):
                                        # Check if it's a high-quality image (not thumbnail)
                                        if 'scontent' in src and len(src) > 50:
                                            image_urls.append(src)
                                            print(f"Extracted image from photo page: {src[:100]}...")
                                            found_image = True
                                            break
                                if found_image:
                                    break
                            except Exception as sel_e:
                                continue
                                
                        # Close the photo page tab
                        self.driver.close()
                        self.driver.switch_to.window(self.driver.window_handles[0])
                        
                        if not found_image:
                            print(f"Could not extract image from photo page: {link}")
                            
                    except Exception as e:
                        print(f"Error processing photo link {link}: {e}")
                        # Make sure we're back on main window
                        try:
                            if len(self.driver.window_handles) > 1:
                                self.driver.close()
                                self.driver.switch_to.window(self.driver.window_handles[0])
                        except:
                            pass
                        
        except Exception as e:
            print(f"Error extracting images from photo links: {e}")
            
        return image_urls

    def fetch_full_article_content(self, links):
        """Fetch full article content from Kuensel links"""
        full_content = ""
        full_title = ""
        
        try:
            # Look for Kuensel links
            kuensel_links = [link for link in links if 'kuenselonline.com' in link or 'kuensel.bt' in link]
            
            if not kuensel_links:
                return full_content, full_title
            
            # Take the first Kuensel link
            article_url = kuensel_links[0]
            print(f"Fetching full article from: {article_url}")
            
            # Set headers to mimic a browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            # Fetch the article
            response = requests.get(article_url, headers=headers, timeout=10)
            if response.status_code == 200:
                # Parse the HTML content
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract title from various possible selectors
                title_selectors = [
                    'h1.entry-title',
                    'h1.post-title', 
                    'h1.article-title',
                    '.title h1',
                    'h1',
                    'title'
                ]
                
                for selector in title_selectors:
                    title_elem = soup.select_one(selector)
                    if title_elem and title_elem.get_text(strip=True):
                        full_title = title_elem.get_text(strip=True)
                        break
                
                # Extract content from various possible selectors
                content_selectors = [
                    '.entry-content',
                    '.post-content',
                    '.article-content',
                    '.content',
                    'article',
                    '.main-content p',
                    '.post-body',
                    '.entry-body'
                ]
                
                for selector in content_selectors:
                    content_elem = soup.select_one(selector)
                    if content_elem:
                        # Get all paragraphs within the content
                        paragraphs = content_elem.find_all('p')
                        if paragraphs:
                            content_text = '\n\n'.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
                            if len(content_text) > len(full_content):
                                full_content = content_text
                        else:
                            # If no paragraphs, get all text
                            text = content_elem.get_text(strip=True)
                            if len(text) > len(full_content):
                                full_content = text
                
                # Clean up the content
                if full_content:
                    # Remove extra whitespace and newlines
                    full_content = re.sub(r'\n+', '\n\n', full_content)
                    full_content = re.sub(r'\s+', ' ', full_content)
                    full_content = full_content.strip()
                    
                print(f"Successfully fetched article content: {len(full_content)} characters")
                
            else:
                print(f"Failed to fetch article: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"Error fetching article content: {e}")
            
        return full_content, full_title

    def is_valid_image_url(self, url):
        """Check if URL is a valid image URL"""
        if not url:
            return False

        # Ignore Facebook static resources and UI elements
        ignore_patterns = [
            'rsrc.php',
            'static.xx.fbcdn.net/rsrc.php',
            'emoji.php',
            'spacer.gif',
            'transparent.gif',
            '/rsrc.php',
            'blank.gif',
            'spinner',
            'loading'
        ]

        if any(pattern in url for pattern in ignore_patterns):
            return False

        # Check if it looks like an image URL
        # Include Facebook CDN patterns and common image extensions
        valid_patterns = [
            'fbcdn.net',
            'facebook.com',
            'cdninstagram.com'
        ]
        
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']
        
        # Must start with http/https
        if not url.startswith(('http://', 'https://')):
            return False
            
        # Must have valid domain or extension
        has_valid_domain = any(pattern in url for pattern in valid_patterns)
        has_image_extension = any(ext in url.lower() for ext in image_extensions)
        
        # Facebook images often don't have extensions but are on fbcdn.net
        # Also check for common Facebook image URL patterns
        fb_image_patterns = [
            'scontent',
            'fbcdn.net/v/t',
            'graph.facebook.com',
            '/photos/',
            '/photo.php'
        ]
        
        has_fb_pattern = any(pattern in url for pattern in fb_image_patterns)
        
        return has_valid_domain or has_image_extension or has_fb_pattern

    def clean_text(self, text):
        """Clean and preprocess text"""
        if not text:
            return ""

        # Decode HTML entities
        text = html.unescape(text)

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()

        # Remove excessive special characters by keeping basic punctuation
        text = re.sub(r'[^\w\s.,!?;:()\-\'\"#@]', ' ', text)

        return text.strip()

    def parse_count(self, count_str):
        """Parse count strings like '1.2K', '5M'"""
        if not count_str:
            return 0

        count_str = str(count_str).upper().strip()

        if 'K' in count_str:
            return int(float(count_str.replace('K', '')) * 1000)
        elif 'M' in count_str:
            return int(float(count_str.replace('M', '')) * 1000000)
        else:
            try:
                return int(float(count_str))
            except:
                return 0

    def is_valid_post(self, post_data):
        """Check if post has meaningful content"""
        content = post_data.get('content', '')
        title = post_data.get('title', '')
        description = post_data.get('description', '')
        
        # Filter out posts with no meaningful content
        if not content or len(content.strip()) < 10:
            return False
            
        # Filter out posts with only dots or minimal content
        content_clean = content.strip()
        if content_clean in ['', '.', '..', '...', '....', '.....']:
            return False
            
        # Filter out posts that are just the title repeated
        if content_clean == title.strip():
            return False
            
        # Filter out very short posts that are likely incomplete
        if len(content_clean) < 15 and not any(char.isalnum() for char in content_clean):
            return False
            
        # Filter out posts with suspiciously generic content
        generic_patterns = [
            'shame for a leader',
            'untitled post',
            'loading...',
            'error',
            'failed to load'
        ]
        
        content_lower = content_clean.lower()
        if any(pattern in content_lower for pattern in generic_patterns):
            return False
            
        # Require at least some meaningful text (letters or numbers)
        if not any(char.isalnum() for char in content_clean):
            return False
            
        # Additional check: if description is just dots, it's likely incomplete
        if description and description.strip() in ['', '.', '..', '...', '....', '.....']:
            # Unless the content is substantial
            if len(content_clean) < 50:
                return False
        
        return True

    def create_post_hash(self, post_data):
        """Create hash to identify duplicate posts"""
        content = post_data.get('content', '')
        title = post_data.get('title', '')
        combined = f"{content}_{title}"
        return hashlib.md5(combined.encode()).hexdigest()

    def remove_duplicates(self):
        """Remove duplicate posts from the list"""
        unique_posts = []
        seen_hashes = set()

        for post in self.posts_data:
            post_hash = self.create_post_hash(post)
            if post_hash not in seen_hashes:
                seen_hashes.add(post_hash)
                unique_posts.append(post)

        self.posts_data = unique_posts
        return len(unique_posts)

    def scrape_posts(self, page_url="https://www.facebook.com/Kuensel", target_count=None, max_scrolls=None): # Fixed URL
        """Main scraping function - implements your 7-step process"""
        if target_count is None:
            target_count = self.config["scraping"]["target_count"]
        if max_scrolls is None:
            max_scrolls = self.config["scraping"]["max_scrolls"]

        print(f"Starting to scrape up to {target_count} posts from {page_url}...")

        # Step 1: Navigate to page
        if not self.navigate_to_page(page_url): # This method is now defined
            return []

        scrolls = 0
        consecutive_empty_scrapes = 0
        max_consecutive_empty = 3

        # Cycle until required number of posts
        while len(self.posts_data) < target_count and scrolls < max_scrolls:
            # 1: Use Selenium to scroll down a little and load new posts
            print(f"Scroll #{scrolls + 1}...")
            self.scroll_page()

            # 1.5: Expand "See more" links to get full content
            if scrolls % 2 == 0:  # Expand every 2nd scroll to avoid too many clicks
                print("Expanding 'See more' links...")
                expanded = self.expand_see_more_links()
                if expanded > 0:
                    time.sleep(2)  # Wait for content to fully load after expansion

            # 2: Extract the HTML of the current page
            html_content = self.get_page_html()

            # 3: Use BeautifulSoup to parse the HTML and extract the required post data
            new_posts = self.extract_posts_with_beautifulsoup(html_content)
            print(f"Extracted {len(new_posts)} raw posts")

            # 4: Store the extracted data in a list (after validation)
            old_count = len(self.posts_data)
            valid_posts_count = 0

            for post in new_posts:
                post_hash = self.create_post_hash(post)
                if post_hash not in self.seen_post_hashes:
                    if self.is_valid_post(post):  
                        self.seen_post_hashes.add(post_hash)
                        self.posts_data.append(post)
                        valid_posts_count += 1
                    else:
                        print(f"Post rejected as invalid: {post.get('title', '')[:30] if post.get('title') else 'No title'}")

            new_count = len(self.posts_data)
            print(f"Found {valid_posts_count} valid posts in this scroll. Total unique posts: {new_count}")

            # Check if we're getting new content
            if new_count == old_count:
                consecutive_empty_scrapes += 1
                if consecutive_empty_scrapes >= max_consecutive_empty:
                    print("No new content found after multiple scrolls. Stopping...")
                    break
            else:
                consecutive_empty_scrapes = 0

            # 6: Remove any duplicate entries from the list
            unique_count = self.remove_duplicates()
            print(f"After deduplication: {unique_count} unique posts")

            scrolls += 1

            # Small delay between scrolls
            time.sleep(1)

        print(f"Scraping complete. Found {len(self.posts_data)} unique posts.")
        return self.posts_data

    def format_for_output(self):
        """Format posts data to match required fields exactly"""
        formatted_posts = []

        for i, post in enumerate(self.posts_data):
            formatted_post = {
                "id": post.get("id", f"post_{i}"),
                "title": post.get("title", ""),
                "description": post.get("description", ""),
                "content": post.get("content", ""),
                "categoryID": post.get("categoryID", "general"),
                "authorId": post.get("authorId", "kuensel"),
                "AuthorName": post.get("authorName", "Kuensel"),
                "attachment": post.get("attachment", {"images": [], "videos": [], "links": []}),
                "createdAt": post.get("createdAt", datetime.now().isoformat()),
                "publishAt": post.get("publishAt", datetime.now().isoformat())
            }
            formatted_posts.append(formatted_post)

        return formatted_posts

    def ensure_output_directory(self):
        """Ensure output directory exists"""
        folder = self.config["output"]["folder"]
        if folder and not os.path.exists(folder):
            os.makedirs(folder)
            print(f"Created directory: {folder}")

    def save_posts_consolidated(self, new_posts):
        """Save posts to a single consolidated file, adding only new ones"""
        consolidated_file = "data/kuensel_posts_master.json"
        
        # Load existing posts if file exists
        existing_posts = []
        existing_ids = set()
        
        if os.path.exists(consolidated_file):
            try:
                with open(consolidated_file, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                    existing_posts = existing_data.get("posts", [])
                    existing_ids = {post.get("id") for post in existing_posts if post.get("id")}
                print(f"Loaded {len(existing_posts)} existing posts from master file")
            except (json.JSONDecodeError, FileNotFoundError):
                print("No existing master file found or file corrupted, starting fresh")
        
        # Filter new posts (only add posts that don't exist)
        truly_new_posts = []
        for post in new_posts:
            if post.get("id") not in existing_ids:
                truly_new_posts.append(post)
        
        if not truly_new_posts:
            print("No new posts to add to master file")
            return consolidated_file
        
        # Combine posts (new posts first to maintain chronological order)
        all_posts = truly_new_posts + existing_posts
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(consolidated_file), exist_ok=True)
        
        # Create final data structure
        final_data = {
            "scraping_session": {
                "timestamp": datetime.now().isoformat(),
                "total_posts": len(all_posts),
                "new_posts_this_session": len(truly_new_posts),
                "existing_posts": len(existing_posts),
                "status": "completed"
            },
            "posts": all_posts
        }
        
        # Save consolidated file
        with open(consolidated_file, 'w', encoding='utf-8') as f:
            json.dump(final_data, f, indent=2, ensure_ascii=False)
        
        print(f"Consolidated data saved to {consolidated_file}")
        print(f"Added {len(truly_new_posts)} new posts to master file")
        print(f"Total posts in master file: {len(all_posts)}")
        
        return consolidated_file

    def save_posts(self, posts, filename=None):
        """Save posts to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            folder = self.config["output"]["folder"]
            prefix = self.config["output"]["filename_prefix"]
            filename = f"{folder}{prefix}_{timestamp}.json"

        # Ensure directory exists
        self.ensure_output_directory()
        directory = os.path.dirname(filename)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

        # Create final data structure
        final_data = {
            "scraping_session": {
                "timestamp": datetime.now().isoformat(),
                "total_posts": len(posts),
                "status": "completed"
            },
            "posts": posts
        }

        # Save to file
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(final_data, f, indent=2, ensure_ascii=False)

        print(f"Data saved to {filename}")
        return filename

    def download_images(self, posts, download_folder="downloaded_images"):
        """Download images from posts"""
        if not self.config["download_images"]:
            return

        if not os.path.exists(download_folder):
            os.makedirs(download_folder)

        downloaded_count = 0
        for i, post in enumerate(posts):
            attachment = post.get("attachment", {})
            images = attachment.get("images", [])

            for j, img_url in enumerate(images):
                try:
                    response = requests.get(img_url, timeout=10)
                    if response.status_code == 200:
                        # Create filename
                        ext = img_url.split('.')[-1].split('?')[0]
                        if not ext or len(ext) > 5:  # Invalid extension
                            ext = 'jpg'
                        filename = f"post_{i}_img_{j}.{ext}"
                        filepath = os.path.join(download_folder, filename)

                        with open(filepath, 'wb') as f:
                            f.write(response.content)
                        downloaded_count += 1
                        print(f"Downloaded: {filename}")
                except Exception as e:
                    print(f"Failed to download image {img_url}: {e}")

        print(f"Downloaded {downloaded_count} images to {download_folder}")

    def close(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()
            print("WebDriver closed")


def main():
    # Check if we've already scraped recently
    last_run_file = "data/last_run.txt"
    current_time = datetime.now()
    
    try:
        with open(last_run_file, 'r') as f:
            last_run = datetime.fromisoformat(f.read().strip())
            time_diff = (current_time - last_run).total_seconds()
            
            # If less than 30 minutes since last run, skip
            if time_diff < 1800:  # 30 minutes = 1800 seconds
                print(f"Last run was only {time_diff} seconds ago. Skipping...")
                return
    except FileNotFoundError:
        pass  # First run, continue

    # Initialize scraper
    scraper = FacebookScraper()

    try:
        # Login to Facebook
        print("Logging in to Facebook...")
        if not scraper.login():
            print("Failed to login.")
            return
            
        # Update last run time
        os.makedirs('data', exist_ok=True)
        with open(last_run_file, 'w') as f:
            f.write(current_time.isoformat())

        # Scrape posts from Kuensel page
        print("Starting to scrape Kuensel Facebook page...")
        # Fixed URL (removed extra spaces)
        posts = scraper.scrape_posts("https://www.facebook.com/Kuensel")

        if not posts:
            print("No posts were scraped.")
            # Save raw data for debugging
            raw_data = {
                "scraping_session": {
                    "timestamp": datetime.now().isoformat(),
                    "total_posts": 0,
                    "status": "no_posts_found",
                    "debug_info": "No valid posts found during scraping"
                },
                "posts": []
            }
            # scraper.save_posts(raw_data, "debug_no_posts.json")
            return

        # Formating data with required fields
        print("Formatting data with required fields...")
        formatted_data = scraper.format_for_output()

        # Download images (False for now)
        scraper.download_images(formatted_data)

        # Save to consolidated master file (single growing file)
        master_filename = scraper.save_posts_consolidated(formatted_data)

        # Generate static API files
        from generate_static_api import generate_static_api
        generate_static_api()

        # Auto-deploy to GitHub Pages
        import subprocess
        import os
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            deploy_script = os.path.join(script_dir, 'auto_deploy.sh')
            if os.path.exists(deploy_script):
                print("Auto-deploying to GitHub Pages...")
                result = subprocess.run([deploy_script], capture_output=True, text=True, cwd=script_dir)
                if result.returncode == 0:
                    print("GitHub Pages deployment initiated")
                else:
                    print(f"Deployment script output: {result.stdout}")
                    if result.stderr:
                        print(f" Deployment error: {result.stderr}")
        except Exception as e:
            print(f"Auto-deployment failed: {e}")

        # Print summary
        print(f"\n=== Scraping Summary ===")
        print(f"Total posts scraped: {len(formatted_data)}")
        print(f"Master data saved to: {master_filename}")

        # Print sample data
        if len(formatted_data) > 0:
            print(f"\n=== Sample Post ===")
            sample = formatted_data[0]
            print(f"ID: {sample['id']}")
            print(f"Title: {sample['title']}")
            print(f"Author: {sample['AuthorName']}")
            if sample['description']:
                print(f"Description: {sample['description']}")
            if sample['content']:
                print(f"Content: {sample['content'][:100]}...")

            # Show attachment info
            attachment = sample['attachment']
            if attachment['images']:
                print(f"Images found: {len(attachment['images'])}")
            if attachment['videos']:
                print(f"Videos found: {len(attachment['videos'])}")
            if attachment['links']:
                print(f"Links found: {len(attachment['links'])}")
        else:
            print("No valid posts found after formatting.")

    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()

    finally:
        scraper.close()


if __name__ == "__main__":
    main()