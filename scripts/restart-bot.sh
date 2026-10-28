#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

bash "$(dirname "$0")/ensure-datastores.sh"

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

if systemctl is-enabled reviewpilot.service >/dev/null 2>&1; then
  sudo systemctl restart reviewpilot.service
  echo "ReviewPilot restarted via systemd (journalctl -u reviewpilot -f)"
  exit 0
fi

pkill -f "python3 -m app.main" 2>/dev/null || true
sleep 1

python3 - <<'PY'
import asyncio
from aiogram import Bot
from app.core.config import get_settings

async def main() -> None:
    bot = Bot(token=get_settings().bot_token)
    await bot.delete_webhook(drop_pending_updates=False)
    wh = await bot.get_webhook_info()
    print(f"Telegram webhook cleared, pending updates: {wh.pending_update_count}")
    await bot.session.close()

asyncio.run(main())
PY

nohup python3 -m app.main >> /tmp/reviewpilot-bot.log 2>&1 &
echo "ReviewPilot started (log: /tmp/reviewpilot-bot.log)"
