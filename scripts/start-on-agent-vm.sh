#!/usr/bin/env bash
# Start ReviewPilot on Cloud Agent VM (tmux). Requires secrets → write-env-from-secrets.sh.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
LOG=/tmp/reviewpilot-bot.log
SESSION=reviewpilot-bot
TMUX=(tmux -f /exec-daemon/tmux.portal.conf)

bash "$ROOT/scripts/ensure-datastores.sh"
if command -v pg_isready >/dev/null && ! pg_isready -q 2>/dev/null; then
  sudo pg_ctlcluster 16 main start 2>/dev/null || true
fi
if command -v pg_isready >/dev/null && pg_isready -q; then
  bash "$ROOT/scripts/setup-local-postgres.sh" || true
fi

if [[ ! -f "$ROOT/.env" ]] || ! grep -qE '^BOT_TOKEN=.+$' "$ROOT/.env" 2>/dev/null; then
  bash "$ROOT/scripts/write-env-from-secrets.sh" || {
    echo "ReviewPilot not started: configure BOT_TOKEN (and FERNET_KEY) in Cloud Agent secrets." | tee -a "$LOG"
    exit 0
  }
fi

pip3 install -q -r "$ROOT/requirements.txt" 2>/dev/null || pip3 install --break-system-packages -q -r "$ROOT/requirements.txt"
python3 -m alembic upgrade head

"${TMUX[@]}" has-session -t "=$SESSION" 2>/dev/null && "${TMUX[@]}" kill-session -t "$SESSION" || true
"${TMUX[@]}" new-session -d -s "$SESSION" -c "$ROOT" -- "${SHELL:-bash}" -l -c "
  export PYTHONUNBUFFERED=1
  exec python3 -m app.main 2>&1 | tee -a $LOG
"
sleep 4
if curl -sf "http://127.0.0.1:${HEALTH_PORT:-8081}/health" >/dev/null 2>&1; then
  echo "ReviewPilot running (tmux session $SESSION, log $LOG)"
else
  echo "ReviewPilot started; health not ready yet — see $LOG"
  tail -20 "$LOG" 2>/dev/null || true
fi
