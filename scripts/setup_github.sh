echo "Setting up GitHub repository..."

# Add all files
git add .

# Commit with a good message
git commit -m "Initial commit: Facebook Scraper with GitHub Pages support

Features:
- Automated Facebook scraping every hour
- Static API generation (JSON files)
- Web frontend for viewing posts
- GitHub Pages deployment
- Auto-deployment after each scrape"

# Push to GitHub
echo "Pushing to GitHub..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo "Successfully pushed to GitHub!"
    echo ""
    echo "repository: https://github.com/SONAMTENZIN7/Facebook_Scrapper"
    echo "Next steps:"
    echo "   1. Go to your repository settings"
    echo "   2. Scroll to 'Pages' section"
    echo "   3. Source: Deploy from a branch"
    echo "   4. Branch: main / (root)"
    echo "   5. Save"
    echo ""
    echo "Your live site will be at:"
    echo "   https://sonamtenzin7.github.io/Facebook_Scrapper/"
else
    echo "Failed to push to GitHub"
    echo "Make sure you've created the repository on GitHub first"
fi
