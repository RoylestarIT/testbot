"""Исходящие уведомления бота: без звука, чтобы не сдвигать чат при работе с меню."""

from __future__ import annotations

from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup


async def send_proactive(
    bot: Bot,
    chat_id: int,
    text: str,
    *,
    reply_markup: InlineKeyboardMarkup | None = None,
) -> None:
    await bot.send_message(
        chat_id,
        text,
        reply_markup=reply_markup,
        disable_notification=True,
    )
