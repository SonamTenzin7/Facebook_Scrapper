#!/bin/bash

# Simple launcher to view Kuensel posts
# This script starts a local web server and opens the browser

PORT=8080
URL="http://localhost:$PORT/frontend.html"

echo "🚀 Starting local server for Kuensel Posts..."

# Check if port is already in use
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; then
    echo "✅ Server already running on port $PORT"
    echo "🌐 Opening browser..."
    open "$URL"
else
    echo "📡 Starting HTTP server on port $PORT..."
    cd "$(dirname "$0")"
    
    # Start server in background
    python3 -m http.server $PORT > /dev/null 2>&1 &
    SERVER_PID=$!
    
    # Wait a moment for server to start
    sleep 2
    
    echo "✅ Server started (PID: $SERVER_PID)"
    echo "🌐 Opening browser..."
    open "$URL"
    
    echo ""
    echo "📰 Your Kuensel Posts are now available at: $URL"
    echo "🔄 Posts auto-update every 30 minutes"
    echo "⏹️  Press Ctrl+C to stop the server"
    
    # Keep script running until user stops it
    trap "echo ''; echo '🛑 Stopping server...'; kill $SERVER_PID; exit 0" INT
    wait $SERVER_PID
fi
