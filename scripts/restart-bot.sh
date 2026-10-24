#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

echo "Applying DB migrations…"
python3 -m alembic upgrade head

python3 - <<'PY'
import asyncio
from app.core.config import get_settings
from app.services.payment.crypto_pay import CryptoPayError, _api_request

async def main() -> None:
    settings = get_settings()
    if not settings.crypto_pay_api_token.strip():
        print("Crypto Pay: not configured (skip)")
        return
    try:
        me = await _api_request(settings, "getMe")
        name = me.get("name") if isinstance(me, dict) else me
        print(f"Crypto Pay OK: {name}")
    except CryptoPayError as exc:
        raise SystemExit(f"Crypto Pay check failed: {exc}") from exc

asyncio.run(main())
PY

pkill -f "python3 -m app.main" 2>/dev/null || true
sleep 1
nohup python3 -m app.main >> /tmp/reviewpilot-bot.log 2>&1 &
echo "ReviewPilot started (log: /tmp/reviewpilot-bot.log)"
