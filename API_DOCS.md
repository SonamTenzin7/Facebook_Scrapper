# 📰 Kuensel Posts API Documentation

A free, public API providing real-time access to Kuensel (Bhutan's national newspaper) Facebook posts. Updated automatically every hour.

## 🌐 Base URL
```
https://sonamtenzin7.github.io/Facebook_Scrapper/static_api/
```

## 📋 Endpoints

https://sonamtenzin7.github.io/Facebook_Scrapper/static_api/posts.json     
https://sonamtenzin7.github.io/Facebook_Scrapper/static_api/categories.json 
https://sonamtenzin7.github.io/Facebook_Scrapper/static_api/stats.json      
https://sonamtenzin7.github.io/Facebook_Scrapper/frontend.html  
### GET `/posts.json`
Returns all posts with complete metadata.

**Response Example:**
```json
{
  "success": true,
  "total_posts": 25,
  "scraping_session": {
    "timestamp": "2025-08-19T14:08:02.403400",
    "total_posts": 25,
    "status": "completed"
  },
  "posts": [
    {
      "id": "unique_post_id",
      "title": "Post headline/title",
      "description": "Short description",
      "content": "Full post content",
      "categoryID": "general",
      "authorId": "kuensel",
      "AuthorName": "Kuensel",
      "createdAt": "2025-08-19T10:30:00",
      "attachment": {
        "images": ["https://...image1.jpg", "https://...image2.jpg"],
        "links": ["https://kuenselonline.com/..."]
      }
    }
  ]
}
```

### GET `/categories.json`
Returns all available post categories.

**Response Example:**
```json
{
  "success": true,
  "categories": ["general", "politics", "business", "sports"]
}
```

### GET `/stats.json`
Returns statistics about the collected data.

**Response Example:**
```json
{
  "success": true,
  "stats": {
    "total_posts": 25,
    "total_images": 45,
    "categories": {
      "general": 20,
      "politics": 5
    },
    "last_updated": "2025-08-19T14:08:02.403400"
  }
}
```

### GET `/posts_general.json`
Returns only posts from the "general" category.

## 🔧 Usage Examples

### JavaScript/TypeScript
```javascript
// Fetch all posts
const posts = await fetch('https://sonamtenzin7.github.io/Facebook_Scrapper/static_api/posts.json')
  .then(res => res.json());

console.log(posts.posts); // Array of post objects
```

### Python
```python
import requests

# Get latest posts
response = requests.get('https://sonamtenzin7.github.io/Facebook_Scrapper/static_api/posts.json')
data = response.json()

for post in data['posts']:
    print(f"Title: {post['title']}")
    print(f"Content: {post['content'][:100]}...")
    print("---")
```

### cURL
```bash
# Get posts via command line
curl -s https://sonamtenzin7.github.io/Facebook_Scrapper/static_api/posts.json | jq '.posts[0]'
```

## 📊 Data Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique post identifier |
| `title` | string | Post headline/title |
| `description` | string | Short description or excerpt |
| `content` | string | Full post content |
| `categoryID` | string | Post category (general, politics, etc.) |
| `authorId` | string | Author identifier |
| `AuthorName` | string | Display name of author |
| `createdAt` | string | ISO 8601 timestamp |
| `attachment.images` | array | Array of image URLs |
| `attachment.links` | array | Array of external links |

## ⚡ Features

- ✅ **No Authentication Required**: Public, free access
- ✅ **CORS Enabled**: Use from any website
- ✅ **Auto-Updated**: Fresh data every hour
- ✅ **Fast & Reliable**: Served by GitHub Pages CDN
- ✅ **Well-Structured**: Consistent JSON format
- ✅ **Rich Metadata**: Images, links, categories, timestamps

## 🚀 Rate Limits & Fair Use

- No rate limits (it's static files!)
- Please cache responses appropriately
- For high-volume usage, consider downloading and self-hosting
- Attribution appreciated but not required

## 📞 Support

This API is automatically generated from Kuensel's Facebook page. For issues or questions, please open an issue on the [GitHub repository](https://github.com/SONAMTENZIN7/Facebook_Scrapper).

## 📄 License

Public domain. Use freely for any purpose.

---

*Last updated: August 2025*
