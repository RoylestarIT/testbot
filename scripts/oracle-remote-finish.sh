#!/usr/bin/env bash
# Run ON the Oracle VM after .env (and optional DB dump) are copied to /opt/reviewpilot.
set -euo pipefail
INSTALL_DIR=/opt/reviewpilot
cd "$INSTALL_DIR"
[[ -f .env ]] || { echo "Place .env in $INSTALL_DIR first"; exit 1; }

bash scripts/setup-postgres-from-env.sh

if [[ -f /tmp/reviewpilot-migrate.sql.gz ]]; then
  DBNAME="$(python3 - <<'PY'
from urllib.parse import urlparse
for line in open(".env", encoding="utf-8"):
    if line.startswith("DATABASE_URL="):
        u = line.split("=", 1)[1].strip().strip('"').strip("'")
        u = u.replace("postgresql+asyncpg://", "postgresql://", 1)
        print(urlparse(u).path.lstrip("/") or "reviewpilot")
        break
PY
)"
  echo "Restoring dump into database ${DBNAME}…"
  gunzip -c /tmp/reviewpilot-migrate.sql.gz | sudo -u postgres psql -v ON_ERROR_STOP=1 -d "$DBNAME"
fi

if ! grep -qE '^FSM_REDIS_URL=.+$' .env; then
  echo "FSM_REDIS_URL=redis://127.0.0.1:6379/0" >> .env
fi

python3 -m alembic upgrade head
bash scripts/install-systemd.sh
sleep 3
curl -sf localhost:8081/health | python3 -m json.tool
rm -f .awaiting-env
