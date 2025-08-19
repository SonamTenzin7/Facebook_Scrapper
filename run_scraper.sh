# Set error handling
set -e
set -x  # Add debug output

# Lock file
LOCK_FILE="/tmp/facebook_scraper.lock"

# Check if the script is already running
if [ -f "$LOCK_FILE" ]; then
    # Check if the process is actually running
    if ps -p $(cat "$LOCK_FILE") > /dev/null 2>&1; then
        echo "Script is already running. Exiting."
        exit 1
    else
        # Remove stale lock file
        rm -f "$LOCK_FILE"
    fi
fi

# Create lock file
echo $$ > "$LOCK_FILE"

# Cleanup function
cleanup() {
    rm -f "$LOCK_FILE"
}

# Set cleanup to run on script exit
trap cleanup EXIT

# Set pyenv environment
export HOME="/Users/sonamtenzin"
export PATH="$HOME/.pyenv/versions/3.10.13/bin:$PATH"
export PYTHONUNBUFFERED=1  # Add this to ensure Python output isn't buffered

# Go to the scraper folder
cd /Users/sonamtenzin/Desktop/AI_ML/Facebook_Scrapper

# Absolute path to log
LOGFILE="/Users/sonamtenzin/Desktop/AI_ML/Facebook_Scrapper/log/scrapper.log"

# Run Python script and log output
{
    echo "===== CRON RUN START ===== $(date)"
    echo "Process ID: $$"
    echo "User: $(whoami)"
    echo "Current directory: $(pwd)"
    echo "Python version: $(python3 --version)"
    echo "PATH: $PATH"
    echo "Chrome location: $(which google-chrome-stable || which chromium || echo 'Chrome not found')"
    echo "Starting Facebook scraper..."
    python3 facebook_scrapper.py 2>&1
    RESULT=$?
    echo "Script exit code: $RESULT"
    echo "Data directory after run:"
    ls -la data/ || echo "Data directory not found"
    echo "===== CRON RUN END ===== $(date)"
    echo ""
} >> "$LOGFILE" 2>&1
