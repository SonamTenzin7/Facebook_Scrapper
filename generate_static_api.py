#!/usr/bin/env python3
"""
Generate simplified static API with only posts that have images
"""

import json
import os
from datetime import datetime

def generate_posts_api():
    """Generate clean posts.json API with only posts that have images"""
    
    # Load master data
    master_file = 'data/kuensel_posts_master.json'
    if not os.path.exists(master_file):
        print(f"Master file not found: {master_file}")
        return
    
    with open(master_file, 'r') as f:
        master_data = json.load(f)
    
    # Handle both array and object structures
    if isinstance(master_data, list):
        all_posts = master_data
        scraping_session = {}
    else:
        all_posts = master_data.get('posts', master_data.get('data', []))
        scraping_session = master_data.get('scraping_session', {})
    
    # Filter posts that have images
    posts_with_images = []
    for post in all_posts:
        attachment = post.get('attachment', {})
        images = attachment.get('images', [])
        
        # Only include posts with images
        if images and len(images) > 0:
            posts_with_images.append(post)
    
    print(f"Total posts: {len(all_posts)}")
    print(f"Posts with images: {len(posts_with_images)}")
    print(f"Posts filtered out: {len(all_posts) - len(posts_with_images)}")
    
    # Create clean API structure
    api_data = {
        "success": True,
        "total_posts": len(posts_with_images),
        "last_updated": datetime.now().isoformat(),
        "filter_applied": "only_posts_with_images",
        "scraping_session": {
            "last_scrape": scraping_session.get('timestamp', ''),
            "status": scraping_session.get('status', 'success'),
            "original_total": len(all_posts),
            "filtered_total": len(posts_with_images)
        },
        "posts": []
    }
    
    # Process posts with clean structure
    for post in posts_with_images:
        attachment = post.get('attachment', {})
        clean_post = {
            "id": post.get('id'),
            "title": post.get('title', '').strip(),
            "content": post.get('content', post.get('description', '')).strip(),
            "category": post.get('categoryID', 'general'),
            "author": post.get('AuthorName', 'Kuensel'),
            "created_at": post.get('createdAt'),
            "published_at": post.get('publishAt'),
            "has_images": True,  # All posts have images now
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
    
    # Sort posts by creation date (newest first)
    api_data["posts"].sort(key=lambda x: x.get('created_at', ''), reverse=True)
    
    # Save clean posts.json
    output_file = 'static_api/posts.json'
    os.makedirs('static_api', exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(api_data, f, indent=2, ensure_ascii=False)
    
    # Statistics
    total_images = sum(post["image_count"] for post in api_data["posts"])
    posts_with_videos = sum(1 for post in api_data["posts"] if post["has_videos"])
    
    print(f"Generated clean posts.json with image filter")
    print(f"   Posts included: {len(api_data['posts'])}")
    print(f"   Total images: {total_images}")
    print(f"   Posts with videos: {posts_with_videos}")
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

if __name__ == "__main__":
    print("Generating simplified static API (images only)...")
    generate_posts_api()
    clean_old_api_files()
    print("API generation completed!")
