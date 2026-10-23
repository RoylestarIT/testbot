#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
DEST="${1:-./backups}"
mkdir -p "$DEST"
TS="$(date +%Y%m%d-%H%M%S)"
if [[ -f reviewpilot.db ]]; then
  cp reviewpilot.db "$DEST/reviewpilot-$TS.db"
  echo "Backup: $DEST/reviewpilot-$TS.db"
else
  echo "reviewpilot.db not found in repo root"
  exit 1
fi
