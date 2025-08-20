#!/usr/bin/env python3
"""
Add the missing nursing post to the master data file
"""

import json
import hashlib
from datetime import datetime

def add_missing_nursing_post():
    """Add the missing nursing post to the master data"""
    
    # Load current master data
    with open('data/kuensel_posts_master.json', 'r') as f:
        data = json.load(f)
    
    # Create the missing nursing post
    nursing_post_content = """𝗡𝗼𝗻-𝘀𝗰𝗶𝗲𝗻𝗰𝗲 𝘀𝘁𝘂𝗱𝗲𝗻𝘁𝘀 𝘀𝗵𝗼𝘄 𝗰𝗼𝗺𝗽𝗲𝘁𝗶𝘁𝗶𝘃𝗲 𝗿𝗲𝘀𝘂𝗹𝘁𝘀 𝗶𝗻 𝗻𝘂𝗿𝘀𝗶𝗻𝗴 Neten Dorji While nursing has been viewed as a profession best suited to students from science backgrounds, educators say that perception is outdated, and that students from arts and commerce streams are proving just as capable. The Apollo Bhutan Institute of Nursing and the Arura Nursing Institute have both begun admitting arts and commerce students to General Nursing and Midwifery (GNM) programmes, aligning with global practices."""
    
    # Generate unique ID for this post
    post_id = hashlib.md5((nursing_post_content + "nursing_education").encode()).hexdigest()[:16]
    
    # Create the post object
    nursing_post = {
        "id": post_id,
        "title": "𝗡𝗼𝗻-𝘀𝗰𝗶𝗲𝗻𝗰𝗲 𝘀𝘁𝘂𝗱𝗲𝗻𝘁𝘀 𝘀𝗵𝗼𝘄 𝗰𝗼𝗺𝗽𝗲𝘁𝗶𝘁𝗶𝘃𝗲 𝗿𝗲𝘀𝘂𝗹𝘁𝘀 𝗶𝗻 𝗻𝘂𝗿𝘀𝗶𝗻𝗴 Neten Dorji While nursing has been viewed as a profession best suited to students from science ba...",
        "description": "𝗡𝗼𝗻-𝘀𝗰𝗶𝗲𝗻𝗰𝗲 𝘀𝘁𝘂𝗱𝗲𝗻𝘁𝘀 𝘀𝗵𝗼𝘄 𝗰𝗼𝗺𝗽𝗲𝘁𝗶𝘁𝗶𝘃𝗲 𝗿𝗲𝘀𝘂𝗹𝘁𝘀 𝗶𝗻 𝗻𝘂𝗿𝘀𝗶𝗻𝗴 Neten Dorji While nursing has been viewed as a profession best suited to students from science backgrounds, educators say that perception is outdated, and that students from arts and commerce streams are proving just as capable. The Apollo Bhutan Institute of Nursing and the Arura Nursing Institute have both begun admitting arts and commerce students to General Nursing and Midwifery (GNM) programmes, aligning with global practices. #nursing #education #healthcare #Bhutan",
        "content": nursing_post_content,
        "categoryID": "news",
        "authorId": "kuensel",
        "AuthorName": "Kuensel",
        "attachment": {
            "images": [],
            "videos": [],
            "links": []
        },
        "createdAt": datetime.now().isoformat(),
        "publishAt": datetime.now().isoformat()
    }
    
    # Check if post already exists (by content similarity)
    exists = False
    for post in data.get('posts', []):
        if 'nursing' in post.get('content', '').lower() and 'non-science' in post.get('content', '').lower():
            exists = True
            break
    
    if not exists:
        # Add the post to the beginning of the posts list (most recent)
        data['posts'].insert(0, nursing_post)
        
        # Update metadata
        if 'scraping_session' in data:
            data['scraping_session']['total_posts'] = len(data['posts'])
            data['scraping_session']['new_posts_this_session'] = data['scraping_session'].get('new_posts_this_session', 0) + 1
            data['scraping_session']['timestamp'] = datetime.now().isoformat()
        
        # Save the updated data
        with open('data/kuensel_posts_master.json', 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Added missing nursing post with ID: {post_id}")
        print(f"📊 Total posts now: {len(data['posts'])}")
        
        # Regenerate static API files
        import subprocess
        try:
            subprocess.run(['python3', 'generate_static_api.py'], check=True)
            print("✅ Regenerated static API files")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to regenerate API files: {e}")
    else:
        print("ℹ️ Nursing post already exists in the data")

if __name__ == "__main__":
    add_missing_nursing_post()
