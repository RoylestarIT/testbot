#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
DEST="${1:-./backups}"
mkdir -p "$DEST"
TS="$(date +%Y%m%d-%H%M%S)"

if [[ -f .env ]]; then
  DATABASE_URL="$(grep -E '^DATABASE_URL=' .env | head -1 | cut -d= -f2- | tr -d '\r' | sed 's/^"//;s/"$//')"
  export DATABASE_URL
fi

if [[ "${DATABASE_URL:-}" == postgresql+asyncpg://* ]]; then
  PGURL="${DATABASE_URL/postgresql+asyncpg/postgresql}"
  OUT="$DEST/reviewpilot-$TS.sql.gz"
  pg_dump "$PGURL" | gzip -c > "$OUT"
  echo "PostgreSQL backup: $OUT"
elif [[ -f reviewpilot.db ]]; then
  cp reviewpilot.db "$DEST/reviewpilot-$TS.db"
  echo "SQLite backup: $DEST/reviewpilot-$TS.db"
else
  echo "No reviewpilot.db and DATABASE_URL is not PostgreSQL"
  exit 1
fi
