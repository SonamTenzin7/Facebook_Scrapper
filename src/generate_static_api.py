#!/usr/bin/env python3
"""
Generate simplified static API with all posts from the scraper
"""

import json
import os
from datetime import datetime

def generate_posts_api():
    """Generate clean posts.json API with all posts from the scraper"""
    
    # Load master data
    master_file = 'data/kuensel_posts_master.json'
    if not os.path.exists(master_file):
        print(f"Master file not found: {master_file}")
        return
    
    with open(master_file, 'r') as f:
        master_data = json.load(f)
    
    # Handle both scraper format and API format
    if isinstance(master_data, list):
        # Old array format
        all_posts = master_data
        scraping_session = {}
    elif "posts" in master_data and isinstance(master_data["posts"], list):
        if "scraping_session" in master_data:
            # Scraper format: {"scraping_session": {...}, "posts": [...]}
            all_posts = master_data.get('posts', [])
            scraping_session = master_data.get('scraping_session', {})
        else:
            # API format: {"success": true, "total_posts": N, "posts": [...]}
            print("Warning: Found API format instead of scraper format in master file")
            all_posts = master_data.get('posts', [])
            scraping_session = {
                "timestamp": master_data.get('last_updated', ''),
                "status": "recovered_from_api_format",
                "total_posts": master_data.get('total_posts', len(all_posts))
            }
    else:
        # Fallback
        all_posts = master_data.get('posts', master_data.get('data', []))
        scraping_session = master_data.get('scraping_session', {})
    
    # Include all posts (not just those with images)
    all_valid_posts = []
    for post in all_posts:
        attachment = post.get('attachment', {})
        images = attachment.get('images', [])
        
        # Include all posts
        all_valid_posts.append(post)
    
    print(f"Total posts: {len(all_posts)}")
    print(f"Posts with images: {sum(1 for post in all_valid_posts if post.get('attachment', {}).get('images'))}")
    print(f"Posts included: {len(all_valid_posts)}")
    
    # Create clean API structure
    api_data = {
        "success": True,
        "total_posts": len(all_valid_posts),
        "last_updated": datetime.now().isoformat(),
        "filter_applied": "all_posts",
        "scraping_session": {
            "last_scrape": scraping_session.get('timestamp', ''),
            "status": scraping_session.get('status', 'success'),
            "original_total": len(all_posts),  # Use actual count, not metadata count
            "filtered_total": len(all_valid_posts)
        },
        "posts": []
    }
    
    # Process all posts with clean structure
    for post in all_valid_posts:
        attachment = post.get('attachment', {})
        has_images = len(attachment.get('images', [])) > 0
        clean_post = {
            "id": post.get('id'),
            "title": post.get('title', '').strip(),
            "content": post.get('content', post.get('description', '')).strip(),
            "category": post.get('categoryID', 'general'),
            "author": post.get('AuthorName', 'Kuensel'),
            "created_at": post.get('createdAt'),
            "published_at": post.get('publishAt'),
            "has_images": has_images,
            "image_count": len(attachment.get('images', [])),
            "has_videos": len(attachment.get('videos', [])) > 0,
            "has_links": len(attachment.get('links', [])) > 0,
            "attachment": {
                "images": attachment.get('images', []),
                "videos": attachment.get('videos', []),
                "links": attachment.get('links', [])
            }
        }
        
        # Add content length for API consumers
        clean_post["content_length"] = len(clean_post["content"])
        
        api_data["posts"].append(clean_post)
    
    # Sort posts by creation date (newest first), handle None values
    api_data["posts"].sort(key=lambda x: x.get('created_at') or '1900-01-01', reverse=True)
    
    # Validate data consistency
    print(f"Validation: Master file has {len(all_posts)} posts, API will have {len(api_data['posts'])} posts")
    if len(all_posts) != len(api_data['posts']):
        print(f"⚠️  Post count mismatch detected!")
    else:
        print("✅ Post counts match between master and API files")
    
    # Save clean posts.json
    output_file = 'static_api/posts.json'
    os.makedirs('static_api', exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(api_data, f, indent=2, ensure_ascii=False)
    
    # Statistics
    total_images = sum(post["image_count"] for post in api_data["posts"])
    posts_with_videos = sum(1 for post in api_data["posts"] if post["has_videos"])
    
    print(f"Generated clean posts.json with all posts")
    print(f"   Posts included: {len(api_data['posts'])}")
    print(f"   Total images: {total_images}")
    print(f"   Posts with videos: {posts_with_videos}")
    print(f"   Posts with images: {sum(1 for post in api_data['posts'] if post['has_images'])}")
    if api_data['posts']:
        avg_length = sum(p['content_length'] for p in api_data['posts']) // len(api_data['posts'])
        print(f"   Average content length: {avg_length} chars")

def clean_old_api_files():
    """Remove redundant API files from static_api directory"""
    
    static_dir = 'static_api'
    if not os.path.exists(static_dir):
        return
    
    # Files to remove (keep only posts.json)
    files_to_remove = [
        'categories.json',
        'posts_advertisement.json', 
        'posts_event.json',
        'posts_general.json',
        'posts_news.json',
        'posts_sports.json',
        'stats.json'
    ]
    
    removed_count = 0
    for filename in files_to_remove:
        filepath = os.path.join(static_dir, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            removed_count += 1
            print(f"Removed: {filename}")
    
    if removed_count > 0:
        print(f"Cleaned up {removed_count} redundant API files")
    else:
        print("No redundant files to remove")

def restore_master_file_format():
    """Restore the proper scraper format to the master file if it got corrupted"""
    master_file = 'data/kuensel_posts_master.json'
    
    if not os.path.exists(master_file):
        print("Master file not found, nothing to restore")
        return
    
    try:
        with open(master_file, 'r') as f:
            data = json.load(f)
        
        # Check if it's in API format (needs restoration)
        if "success" in data and "filter_applied" in data:
            print("Restoring master file from API format to scraper format...")
            
            # Convert back to scraper format
            scraper_format = {
                "scraping_session": {
                    "timestamp": data.get('last_updated', datetime.now().isoformat()),
                    "total_posts": data.get('total_posts', len(data.get('posts', []))),
                    "status": "restored_from_api_format"
                },
                "posts": data.get('posts', [])
            }
            
            # Backup the API format file
            backup_file = f"{master_file}.api_format_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            os.rename(master_file, backup_file)
            print(f"API format backed up to: {backup_file}")
            
            # Save in proper scraper format
            with open(master_file, 'w', encoding='utf-8') as f:
                json.dump(scraper_format, f, indent=2, ensure_ascii=False)
            
            print(f"Master file restored to scraper format with {len(scraper_format['posts'])} posts")
            return True
            
    except Exception as e:
        print(f"Error restoring master file: {e}")
        return False
    
    return False

def generate_static_api():
    """Main function called by the scraper to generate static API files"""
    print("Generating simplified static API (images only)...")
    
    # First, try to restore master file format if needed
    restore_master_file_format()
    
    generate_posts_api()
    clean_old_api_files()
    print("API generation completed!")

if __name__ == "__main__":
    generate_static_api()
