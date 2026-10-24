from __future__ import annotations

from aiogram import Bot

from app.core.config import get_settings


async def notify_admins(bot: Bot, text: str) -> None:
    settings = get_settings()
    for admin_id in settings.admin_ids:
        try:
            await bot.send_message(admin_id, f"🛠 <b>Admin log</b>\n\n{text}")
        except Exception:
            continue
