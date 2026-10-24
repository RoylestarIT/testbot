#!/usr/bin/env bash
# Fallback when systemd is unavailable: restart bot after crash (still dies if the whole VM stops).
set -euo pipefail
cd "$(dirname "$0")/.."
bash "$(dirname "$0")/ensure-datastores.sh"
export PYTHONUNBUFFERED=1
while true; do
  echo "$(date -Is) starting app.main…"
  python3 -m alembic upgrade head
  python3 -m app.main
  echo "$(date -Is) bot exited, restart in 10s…"
  sleep 10
done
