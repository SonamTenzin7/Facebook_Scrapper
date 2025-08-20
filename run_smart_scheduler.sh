cd "$(dirname "$0")"
python3 smart_scheduler.py --once >> log/scheduler.log 2>&1
