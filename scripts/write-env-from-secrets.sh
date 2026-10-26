#!/usr/bin/env bash
# Build /workspace/.env from process environment (Cursor Cloud Agent secrets → env vars).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
OUT="$ROOT/.env"
EXAMPLE="$ROOT/.env.example"

python3 - <<'PY'
import os
import re
from pathlib import Path

root = Path(".")
example = root / ".env.example"
out = root / ".env"
keys: list[str] = []
for line in example.read_text(encoding="utf-8").splitlines():
    m = re.match(r"^([A-Z][A-Z0-9_]*)=", line)
    if m:
        keys.append(m.group(1))

lines: list[str] = []
for key in keys:
    val = os.environ.get(key)
    if val is not None and str(val).strip() != "":
        lines.append(f"{key}={val}")

if not any(l.startswith("BOT_TOKEN=") for l in lines):
    raise SystemExit(
        "BOT_TOKEN is not set in the environment. "
        "Add secrets in Cursor → Cloud Agents → Environment → Secrets, then restart the agent."
    )

# Local defaults for this VM when not provided
defaults = {
    "DATABASE_URL": "postgresql+asyncpg://reviewpilot:reviewpilot@127.0.0.1:5432/reviewpilot",
    "FSM_REDIS_URL": "redis://127.0.0.1:6379/0",
    "HEALTH_PORT": "8081",
    "LOG_LEVEL": "INFO",
}
present = {l.split("=", 1)[0] for l in lines}
for k, v in defaults.items():
    if k not in present:
        lines.append(f"{k}={v}")

out.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"Wrote {out} ({len(lines)} keys, secrets not printed)")
PY
