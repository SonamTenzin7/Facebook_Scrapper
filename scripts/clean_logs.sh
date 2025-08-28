#!/bin/bash

# Log rotation script for Facebook Scrapper
# This script archives old logs and creates fresh log files

echo "Starting log cleanup..."

# Create archive directory if it doesn't exist
mkdir -p log/archive

# Get current timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Archive existing logs if they're not empty
if [ -s log/scrapper.log ]; then
    echo "Archiving scrapper.log..."
    cp log/scrapper.log log/archive/scrapper_${TIMESTAMP}.log
    echo "Log cleaned on $(date)" > log/scrapper.log
fi

if [ -s log/launchd.log ]; then
    echo "Archiving launchd.log..."
    cp log/launchd.log log/archive/launchd_${TIMESTAMP}.log
    echo "Log cleaned on $(date)" > log/launchd.log
fi

if [ -s log/launchd_error.log ]; then
    echo "Archiving launchd_error.log..."
    cp log/launchd_error.log log/archive/launchd_error_${TIMESTAMP}.log
    echo "Log cleaned on $(date)" > log/launchd_error.log
fi

# Clean up old archives (keep only last 10 files of each type)
echo "Cleaning old archives..."
ls -t log/archive/scrapper_*.log 2>/dev/null | tail -n +11 | xargs -r rm
ls -t log/archive/launchd_*.log 2>/dev/null | tail -n +11 | xargs -r rm
ls -t log/archive/launchd_error_*.log 2>/dev/null | tail -n +11 | xargs -r rm

echo "Log cleanup complete!"
echo "Current log sizes:"
ls -lah log/*.log
echo "Archived logs:"
ls -lah log/archive/ | tail -n +4
