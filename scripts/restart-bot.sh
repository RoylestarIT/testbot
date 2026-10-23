#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
pkill -f "python3 -m app.main" 2>/dev/null || true
sleep 1
nohup python3 -m app.main >> /tmp/reviewpilot-bot.log 2>&1 &
echo "ReviewPilot started (log: /tmp/reviewpilot-bot.log)"
