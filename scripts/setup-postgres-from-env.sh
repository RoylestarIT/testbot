#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
[[ -f .env ]] || { echo "Missing .env"; exit 1; }

python3 - <<'PY'
import re, subprocess
from urllib.parse import unquote, urlparse

text = open(".env", encoding="utf-8").read()
m = re.search(r"^DATABASE_URL=(.*)$", text, re.M)
if not m:
    raise SystemExit("DATABASE_URL not in .env")
url = m.group(1).strip().strip('"').strip("'")
url = url.replace("postgresql+asyncpg://", "postgresql://", 1)
p = urlparse(url)
user = unquote(p.username or "")
password = unquote(p.password or "")
db = (p.path or "/reviewpilot").lstrip("/") or "reviewpilot"
host = p.hostname or "localhost"
if host not in ("localhost", "127.0.0.1"):
    print(f"DATABASE_URL host is {host}; skip local postgres setup")
    raise SystemExit(0)
if not user:
    raise SystemExit("DATABASE_URL must include username")

def psql(sql: str) -> None:
    subprocess.run(["sudo", "-u", "postgres", "psql", "-v", "ON_ERROR_STOP=1", "-c", sql], check=True)

psql(
    "DO $$ BEGIN "
    f"IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '{user}') THEN "
    f"CREATE ROLE {user} LOGIN PASSWORD '{password.replace(chr(39), chr(39)*2)}'; "
    f"ELSE ALTER ROLE {user} WITH PASSWORD '{password.replace(chr(39), chr(39)*2)}'; "
    "END IF; END $$;"
)
exists = subprocess.run(
    ["sudo", "-u", "postgres", "psql", "-tAc", f"SELECT 1 FROM pg_database WHERE datname='{db}'"],
    capture_output=True,
    text=True,
    check=True,
).stdout.strip()
if exists != "1":
    psql(f"CREATE DATABASE {db} OWNER {user};")
psql(f"GRANT ALL PRIVILEGES ON DATABASE {db} TO {user};")
print(f"PostgreSQL ready: user={user} db={db}")
PY
