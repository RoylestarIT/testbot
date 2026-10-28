#!/usr/bin/env bash
# Install ReviewPilot as a systemd unit (24/7: restart on crash + enable on boot).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
UNIT=/etc/systemd/system/reviewpilot.service

if ! command -v systemctl >/dev/null; then
  echo "systemctl not found. Deploy on a normal Linux VPS (Ubuntu/Debian with systemd)."
  exit 1
fi
if ! systemctl >/dev/null 2>&1; then
  echo "systemd is not PID 1 on this machine (e.g. Cloud Agent dev VM)."
  echo "For 24/7: rent a VPS, clone the repo, copy .env, run ./scripts/install-systemd.sh there."
  echo "This VM cannot keep the bot running when the agent session ends."
  exit 1
fi

TMP="$(mktemp)"
sed "s|WorkingDirectory=/workspace|WorkingDirectory=${ROOT}|g" "$ROOT/deploy/reviewpilot.service" >"$TMP"
sed -i "s|/workspace/scripts/|${ROOT}/scripts/|g" "$TMP"

sudo cp "$TMP" "$UNIT"
rm -f "$TMP"
sudo systemctl daemon-reload
sudo systemctl enable reviewpilot.service

# Stop one-off nohup instance if present
pkill -f "python3 -m app.main" 2>/dev/null || true
sleep 1

sudo systemctl restart reviewpilot.service
sudo systemctl --no-pager status reviewpilot.service
echo ""
echo "Logs: journalctl -u reviewpilot -f"
echo "Health: curl -s localhost:8081/health"
