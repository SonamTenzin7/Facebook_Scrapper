import json
import os
import glob
from datetime import datetime

def generate_static_api():
    """Generate static JSON files for API endpoints"""
    DATA_FOLDER = "data"
    OUTPUT_FOLDER = "static_api"
    
    # Create output directory
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    
    def get_data_file():
        """Get the master data file or fallback to latest individual file"""
        # First try the master file
        master_file = os.path.join(DATA_FOLDER, "kuensel_posts_master.json")
        if os.path.exists(master_file):
            return master_file
            
        # Fallback to latest individual file
        pattern = os.path.join(DATA_FOLDER, "kuensel_posts_*.json")
        files = glob.glob(pattern)
        if not files:
            return None
        return max(files, key=os.path.getctime)
    
    def load_data_file(filepath):
        """Load and return JSON data from file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            return {"error": str(e)}
    
    # Get data (prefer master file)
    data_file = get_data_file()
    if not data_file:
        print("No data files found")
        return
    
    data = load_data_file(data_file)
    if "error" in data:
        print(f"Error loading data: {data['error']}")
        return
    
    posts = data.get("posts", [])
    
    # Generate posts.json
    posts_data = {
        "success": True,
        "total_posts": len(posts),
        "scraping_session": data.get("scraping_session", {}),
        "posts": posts,
        "generated_at": datetime.now().isoformat()
    }
    
    with open(os.path.join(OUTPUT_FOLDER, "posts.json"), 'w', encoding='utf-8') as f:
        json.dump(posts_data, f, indent=2, ensure_ascii=False)
    
    # Generate categories.json
    categories = list(set(post.get("categoryID", "general") for post in posts))
    categories_data = {
        "success": True,
        "categories": categories,
        "generated_at": datetime.now().isoformat()
    }
    
    with open(os.path.join(OUTPUT_FOLDER, "categories.json"), 'w', encoding='utf-8') as f:
        json.dump(categories_data, f, indent=2, ensure_ascii=False)
    
    # Generate stats.json
    categories_count = {}
    total_images = 0
    total_videos = 0
    
    for post in posts:
        category = post.get("categoryID", "general")
        categories_count[category] = categories_count.get(category, 0) + 1
        
        attachment = post.get("attachment", {})
        total_images += len(attachment.get("images", []))
        total_videos += len(attachment.get("videos", []))
    
    stats_data = {
        "success": True,
        "stats": {
            "total_posts": len(posts),
            "categories": categories_count,
            "total_images": total_images,
            "total_videos": total_videos,
            "last_updated": data.get("scraping_session", {}).get("timestamp", "Unknown")
        },
        "generated_at": datetime.now().isoformat()
    }
    
    with open(os.path.join(OUTPUT_FOLDER, "stats.json"), 'w', encoding='utf-8') as f:
        json.dump(stats_data, f, indent=2, ensure_ascii=False)
    
    # Generate by category files
    for category in categories:
        category_posts = [post for post in posts if post.get("categoryID") == category]
        category_data = {
            "success": True,
            "category": category,
            "total_posts": len(category_posts),
            "posts": category_posts,
            "generated_at": datetime.now().isoformat()
        }
        
        with open(os.path.join(OUTPUT_FOLDER, f"posts_{category}.json"), 'w', encoding='utf-8') as f:
            json.dump(category_data, f, indent=2, ensure_ascii=False)
    
    print(f"Static API files generated in {OUTPUT_FOLDER}/")
    print(f"- posts.json ({len(posts)} posts)")
    print(f"- categories.json ({len(categories)} categories)")
    print(f"- stats.json")
    for category in categories:
        category_count = len([p for p in posts if p.get("categoryID") == category])
        print(f"- posts_{category}.json ({category_count} posts)")

if __name__ == "__main__":
    generate_static_api()
