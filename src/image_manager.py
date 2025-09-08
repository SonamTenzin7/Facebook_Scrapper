#!/usr/bin/env python3
"""
Image Manager for Downloaded Facebook Images
Provides utilities to access, serve, and manage downloaded images
"""

import os
import json
import glob
from datetime import datetime
from pathlib import Path
import mimetypes
from urllib.parse import quote
import base64

class ImageManager:
    def __init__(self, images_folder="images", data_folder="data"):
        self.images_folder = images_folder
        self.data_folder = data_folder
        self.master_file = os.path.join(data_folder, "kuensel_posts_master.json")
    
    def get_all_downloaded_images(self):
        """Get list of all downloaded images with metadata"""
        images = []
        
        # Search all date folders
        for date_folder in glob.glob(os.path.join(self.images_folder, "*")):
            if os.path.isdir(date_folder):
                date_name = os.path.basename(date_folder)
                
                # Find all images in this date folder
                for img_file in glob.glob(os.path.join(date_folder, "*.jpg")):
                    img_file = glob.glob(os.path.join(date_folder, "*.png")) + \
                              glob.glob(os.path.join(date_folder, "*.gif")) + \
                              glob.glob(os.path.join(date_folder, "*.webp"))
                
                # Get all image files
                for pattern in ["*.jpg", "*.jpeg", "*.png", "*.gif", "*.webp"]:
                    for img_file in glob.glob(os.path.join(date_folder, pattern)):
                        metadata_file = img_file.replace(
                            f".{img_file.split('.')[-1]}", "_metadata.txt"
                        )
                        
                        img_info = {
                            'filename': os.path.basename(img_file),
                            'full_path': os.path.abspath(img_file),
                            'date_folder': date_name,
                            'size': os.path.getsize(img_file),
                            'modified': datetime.fromtimestamp(os.path.getmtime(img_file)),
                            'metadata': {}
                        }
                        
                        # Load metadata if available
                        if os.path.exists(metadata_file):
                            try:
                                with open(metadata_file, 'r') as f:
                                    for line in f:
                                        if ':' in line:
                                            key, value = line.split(':', 1)
                                            img_info['metadata'][key.strip()] = value.strip()
                            except Exception:
                                pass
                        
                        images.append(img_info)
        
        return sorted(images, key=lambda x: x['modified'], reverse=True)
    
    def get_images_for_post(self, post_id):
        """Get all images for a specific post ID"""
        all_images = self.get_all_downloaded_images()
        return [img for img in all_images if post_id in img['filename']]
    
    def get_image_as_base64(self, image_path):
        """Get image as base64 string for embedding"""
        try:
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            # Get MIME type
            mime_type, _ = mimetypes.guess_type(image_path)
            if not mime_type:
                mime_type = 'image/jpeg'  # default
            
            # Encode to base64
            b64_data = base64.b64encode(image_data).decode('utf-8')
            return f"data:{mime_type};base64,{b64_data}"
        except Exception as e:
            print(f"Error converting image to base64: {e}")
            return None
    
    def create_local_image_urls(self):
        """Create mapping of post IDs to local image paths for API"""
        image_mapping = {}
        
        for img_info in self.get_all_downloaded_images():
            # Extract post ID from filename
            filename = img_info['filename']
            if 'kuensel_' in filename:
                try:
                    # Format: kuensel_[postID]_img[number]_[timestamp].[ext]
                    post_id = filename.split('_')[1]
                    if post_id not in image_mapping:
                        image_mapping[post_id] = []
                    
                    # Create relative path for web serving
                    relative_path = os.path.join(
                        img_info['date_folder'],
                        img_info['filename']
                    ).replace('\\', '/')
                    
                    image_mapping[post_id].append({
                        'local_path': img_info['full_path'],
                        'relative_path': f"images/{relative_path}",
                        'filename': img_info['filename'],
                        'size': img_info['size'],
                        'metadata': img_info['metadata']
                    })
                except Exception:
                    continue
        
        return image_mapping
    
    def update_posts_with_local_images(self):
        """Update the master JSON file to include local image paths"""
        if not os.path.exists(self.master_file):
            print(f"Master file not found: {self.master_file}")
            return False
        
        try:
            # Load master file
            with open(self.master_file, 'r') as f:
                data = json.load(f)
            
            # Get image mapping
            image_mapping = self.create_local_image_urls()
            
            # Update posts with local image information
            updated_count = 0
            for post in data.get('posts', []):
                post_id = post.get('id')
                if post_id and post_id in image_mapping:
                    if 'local_images' not in post:
                        post['local_images'] = image_mapping[post_id]
                        updated_count += 1
                    else:
                        # Update existing local images info
                        post['local_images'] = image_mapping[post_id]
            
            # Save updated file
            backup_file = f"{self.master_file}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            os.rename(self.master_file, backup_file)
            
            with open(self.master_file, 'w') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Updated {updated_count} posts with local image paths")
            print(f"📁 Backup saved: {backup_file}")
            return True
            
        except Exception as e:
            print(f"Error updating posts: {e}")
            return False
    
    def generate_image_gallery_html(self, output_file="image_gallery.html"):
        """Generate an HTML gallery of all downloaded images"""
        images = self.get_all_downloaded_images()
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kuensel Images Gallery</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .gallery {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }}
        .image-card {{ border: 1px solid #ddd; border-radius: 8px; padding: 15px; }}
        .image-card img {{ max-width: 100%; height: auto; border-radius: 4px; }}
        .image-info {{ margin-top: 10px; font-size: 12px; color: #666; }}
        .post-id {{ font-weight: bold; color: #333; }}
        h1 {{ text-align: center; color: #333; }}
        .stats {{ text-align: center; margin: 20px 0; color: #666; }}
    </style>
</head>
<body>
    <h1>🖼️ Kuensel Facebook Images Gallery</h1>
    <div class="stats">
        <p>Total Images: {len(images)} | Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    <div class="gallery">
"""
        
        for img in images:
            post_id = img['metadata'].get('Post ID', 'Unknown')
            img_url = img['metadata'].get('Image URL', 'No URL')
            download_date = img['metadata'].get('Downloaded', 'Unknown')
            file_size = f"{img['size']:,} bytes"
            
            html_content += f"""
        <div class="image-card">
            <img src="{img['full_path']}" alt="Post {post_id}" loading="lazy">
            <div class="image-info">
                <div class="post-id">Post ID: {post_id}</div>
                <div>File: {img['filename']}</div>
                <div>Size: {file_size}</div>
                <div>Downloaded: {download_date}</div>
                <div>Folder: {img['date_folder']}</div>
            </div>
        </div>
"""
        
        html_content += """
    </div>
</body>
</html>"""
        
        with open(output_file, 'w') as f:
            f.write(html_content)
        
        print(f"📄 Generated gallery: {output_file}")
        return output_file

def main():
    """Command line interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Manage downloaded Facebook images")
    parser.add_argument('--list', action='store_true', help='List all downloaded images')
    parser.add_argument('--post-id', help='Show images for specific post ID')
    parser.add_argument('--update-json', action='store_true', help='Update master JSON with local image paths')
    parser.add_argument('--gallery', help='Generate HTML gallery (specify output filename)')
    parser.add_argument('--stats', action='store_true', help='Show download statistics')
    
    args = parser.parse_args()
    
    manager = ImageManager()
    
    if args.list:
        images = manager.get_all_downloaded_images()
        print(f"\n📸 Found {len(images)} downloaded images:")
        for img in images:
            print(f"  📁 {img['filename']} ({img['size']:,} bytes) - {img['date_folder']}")
    
    elif args.post_id:
        images = manager.get_images_for_post(args.post_id)
        print(f"\n🔍 Images for post {args.post_id}:")
        for img in images:
            print(f"  📸 {img['filename']} - {img['full_path']}")
    
    elif args.update_json:
        manager.update_posts_with_local_images()
    
    elif args.gallery:
        manager.generate_image_gallery_html(args.gallery)
    
    elif args.stats:
        images = manager.get_all_downloaded_images()
        total_size = sum(img['size'] for img in images)
        dates = set(img['date_folder'] for img in images)
        
        print(f"\n📊 Download Statistics:")
        print(f"  Total Images: {len(images)}")
        print(f"  Total Size: {total_size:,} bytes ({total_size/1024/1024:.1f} MB)")
        print(f"  Date Folders: {len(dates)}")
        print(f"  Folders: {', '.join(sorted(dates))}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
