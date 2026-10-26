#!/usr/bin/env bash
set -euo pipefail
USER=reviewpilot
PASS=reviewpilot
DB=reviewpilot

sudo -u postgres psql -v ON_ERROR_STOP=1 <<SQL
DO \$\$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '${USER}') THEN
    CREATE ROLE ${USER} LOGIN PASSWORD '${PASS}';
  END IF;
END
\$\$;
SELECT 'CREATE DATABASE ${DB} OWNER ${USER}'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '${DB}')\gexec
GRANT ALL PRIVILEGES ON DATABASE ${DB} TO ${USER};
SQL
echo "Local PostgreSQL: postgresql+asyncpg://${USER}:${PASS}@127.0.0.1:5432/${DB}"
