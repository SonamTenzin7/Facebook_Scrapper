from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
import glob
from datetime import datetime

app = Flask(__name__)
CORS(app)  

DATA_FOLDER = "data"

def get_latest_data_file():
    """Get the most recent JSON data file"""
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

@app.route('/api/posts', methods=['GET'])
def get_posts():
    """Get all posts with optional filtering"""
    try:
        # Get query parameters
        category = request.args.get('category', None)
        limit = request.args.get('limit', None)
        
        # Get latest data file
        latest_file = get_latest_data_file()
        if not latest_file:
            return jsonify({"error": "No data files found"}), 404
        
        # Load data
        data = load_data_file(latest_file)
        if "error" in data:
            return jsonify(data), 500
        
        posts = data.get("posts", [])
        
        # Filter by category if specified
        if category:
            posts = [post for post in posts if post.get("categoryID") == category]
        
        # Limit results if specified
        if limit:
            try:
                limit = int(limit)
                posts = posts[:limit]
            except ValueError:
                pass
        
        return jsonify({
            "success": True,
            "total_posts": len(posts),
            "scraping_session": data.get("scraping_session", {}),
            "posts": posts
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/posts/<post_id>', methods=['GET'])
def get_post_by_id(post_id):
    """Get a specific post by ID"""
    try:
        latest_file = get_latest_data_file()
        if not latest_file:
            return jsonify({"error": "No data files found"}), 404
        
        data = load_data_file(latest_file)
        if "error" in data:
            return jsonify(data), 500
        
        posts = data.get("posts", [])
        post = next((p for p in posts if p.get("id") == post_id), None)
        
        if not post:
            return jsonify({"error": "Post not found"}), 404
        
        return jsonify({
            "success": True,
            "post": post
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Get all available categories"""
    try:
        latest_file = get_latest_data_file()
        if not latest_file:
            return jsonify({"error": "No data files found"}), 404
        
        data = load_data_file(latest_file)
        if "error" in data:
            return jsonify(data), 500
        
        posts = data.get("posts", [])
        categories = list(set(post.get("categoryID", "general") for post in posts))
        
        return jsonify({
            "success": True,
            "categories": categories
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get statistics about the scraped data"""
    try:
        latest_file = get_latest_data_file()
        if not latest_file:
            return jsonify({"error": "No data files found"}), 404
        
        data = load_data_file(latest_file)
        if "error" in data:
            return jsonify(data), 500
        
        posts = data.get("posts", [])
        
        # Calculate stats
        categories_count = {}
        total_images = 0
        total_videos = 0
        
        for post in posts:
            category = post.get("categoryID", "general")
            categories_count[category] = categories_count.get(category, 0) + 1
            
            attachment = post.get("attachment", {})
            total_images += len(attachment.get("images", []))
            total_videos += len(attachment.get("videos", []))
        
        return jsonify({
            "success": True,
            "stats": {
                "total_posts": len(posts),
                "categories": categories_count,
                "total_images": total_images,
                "total_videos": total_videos,
                "last_updated": data.get("scraping_session", {}).get("timestamp", "Unknown")
            }
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
