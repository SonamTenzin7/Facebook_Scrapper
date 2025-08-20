#!/usr/bin/env python3
"""
Comment Cleanup Script for Facebook Scraper
Removes comment-like posts from scraped data
"""

import json
import re
import os
from datetime import datetime

def is_comment_like_post(post):
    """Check if a post looks like a comment rather than news"""
    content = post.get('content', '').strip()
    title = post.get('title', '').strip()
    description = post.get('description', '').strip()
    
    # Check for very short content
    if len(content) < 25:
        return True
    
    # Check for comment patterns
    comment_patterns = [
        r'^how about.{1,30}\?*$',        # "How about closing AWP?"
        r'^what about.{1,30}\?*$',       # "What about this?"
        r'^why not.{1,30}\?*$',          # "Why not do this?"
        r'^[a-zA-Z\s]{1,20}\?+$',        # Short questions like "Really???"
        r'^(ok|okay|yes|no|true|false|really|wow|nice|good|bad)[\.\!\?]*$',  # Single word responses
        r'^\w{1,10}[\.\!\?]+$',          # Very short exclamations
    ]
    
    for pattern in comment_patterns:
        if re.search(pattern, content.lower()):
            return True
    
    # Check if description is just punctuation
    if description in ['?', '??', '???', '.', '..', '...']:
        return True
    
    # Check if no meaningful attachments
    attachments = post.get('attachment', {})
    has_media = bool(attachments.get('images') or 
                    attachments.get('videos') or 
                    attachments.get('links'))
    
    # Very short posts without media are likely comments
    if len(content) < 50 and not has_media:
        return True
    
    return False

def cleanup_comments(file_path):
    """Remove comment-like posts from the master file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        original_count = len(data.get('posts', []))
        
        # Filter out comment-like posts
        cleaned_posts = []
        removed_posts = []
        
        for post in data.get('posts', []):
            if is_comment_like_post(post):
                removed_posts.append(post)
                print(f"🗑️  Removing comment: '{post.get('title', 'No title')[:50]}'")
            else:
                cleaned_posts.append(post)
        
        # Update data
        data['posts'] = cleaned_posts
        
        # Update session info
        if 'scraping_session' in data:
            data['scraping_session']['total_posts'] = len(cleaned_posts)
            data['scraping_session']['timestamp'] = datetime.now().isoformat()
        
        # Save cleaned data
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        removed_count = len(removed_posts)
        final_count = len(cleaned_posts)
        
        print(f"✅ Cleanup complete:")
        print(f"   Original posts: {original_count}")
        print(f"   Removed comments: {removed_count}")
        print(f"   Final posts: {final_count}")
        
        return removed_count > 0
        
    except Exception as e:
        print(f"❌ Error cleaning comments: {e}")
        return False

if __name__ == "__main__":
    master_file = "data/kuensel_posts_master.json"
    
    if os.path.exists(master_file):
        print("🧹 Starting comment cleanup...")
        changed = cleanup_comments(master_file)
        
        if changed:
            print("📊 Regenerating static API files...")
            os.system("python generate_static_api.py")
            print("✅ Cleanup completed!")
        else:
            print("✅ No comments found to remove.")
    else:
        print(f"❌ Master file not found: {master_file}")
