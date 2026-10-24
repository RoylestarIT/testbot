from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta

from aiogram import Bot
from loguru import logger

from app.core.config import Settings, get_settings
from app.tasks.poller import get_poller_health

_last_alert_at: datetime | None = None


async def poller_health_alert_once(bot: Bot, settings: Settings | None = None) -> None:
    global _last_alert_at
    settings = settings or get_settings()
    health = get_poller_health()
    last_ok_raw = health.get("last_ok_at")
    if not last_ok_raw:
        return
    try:
        last_ok = datetime.fromisoformat(str(last_ok_raw))
    except ValueError:
        return
    if last_ok.tzinfo is None:
        last_ok = last_ok.replace(tzinfo=UTC)
    stale_min = max(15, settings.poller_stale_minutes)
    if datetime.now(UTC) - last_ok < timedelta(minutes=stale_min):
        return
    now = datetime.now(UTC)
    if _last_alert_at and now - _last_alert_at < timedelta(hours=1):
        return
    text = (
        f"⚠️ <b>Poller не обновлялся</b> &gt; {stale_min} мин.\n"
        f"Последний OK: <code>{last_ok.isoformat()}</code>\n"
        f"Ошибка: {health.get('last_error') or '—'}"
    )
    for admin_id in settings.admin_ids:
        try:
            await bot.send_message(admin_id, text)
        except Exception:
            logger.warning("poller health alert failed admin={}", admin_id)
    _last_alert_at = now


async def poller_health_alert_loop(bot: Bot, settings: Settings | None = None) -> None:
    settings = settings or get_settings()
    interval = max(300, settings.poll_interval_minutes * 60 // 2)
    logger.info("Poller health alert loop started interval_sec={}", interval)
    while True:
        try:
            await poller_health_alert_once(bot, settings)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("poller health alert iteration failed")
        await asyncio.sleep(interval)
