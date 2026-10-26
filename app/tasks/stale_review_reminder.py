from __future__ import annotations

import asyncio
from datetime import UTC, datetime

from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from loguru import logger
from sqlalchemy import select

from app.bot.ui import BRAND, ICON, REVIEWS_HUB_BUTTON
from app.bot.utils.proactive_notify import send_proactive
from app.core.config import Settings, get_settings
from app.db.models import User
from app.db.repositories.review import ReviewRepository
from app.db.repositories.user import UserRepository
from app.db.session import get_session_factory


def _stale_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=REVIEWS_HUB_BUTTON, callback_data="review:mp:list")],
            [InlineKeyboardButton(text="🏠 Сводка", callback_data="menu:dashboard")],
        ]
    )


async def send_stale_reminders_once(bot: Bot, settings: Settings | None = None) -> None:
    settings = settings or get_settings()
    if datetime.now(UTC).hour != settings.stale_reminder_hour_utc:
        return

    session_factory = get_session_factory()
    now = datetime.now(UTC)

    async with session_factory() as session:
        result = await session.execute(select(User).where(User.notify_stale_reviews.is_(True)))
        users = list(result.scalars().all())

    for user in users:
        if user.last_stale_reminder_at and user.last_stale_reminder_at.date() == now.date():
            continue

        async with session_factory() as session:
            stale_count = await ReviewRepository(session).count_stale_new_for_user(
                user.id,
                older_than_hours=settings.stale_review_hours,
            )
            if stale_count <= 0:
                continue
            db_user = await UserRepository(session).get_by_id(user.id)
            if db_user is None:
                continue
            db_user.last_stale_reminder_at = now
            await session.commit()

        hours = settings.stale_review_hours
        text = (
            f"{ICON} <b>{BRAND}</b>\n"
            f"⏳ В очереди <b>{stale_count}</b> отзыв(ов) без ответа "
            f"больше <b>{hours}</b> ч.\n\n"
            "<i>Откройте очередь и ответьте, пока покупатель не остыл.</i>"
        )
        try:
            await send_proactive(bot, user.tg_id, text, reply_markup=_stale_keyboard())
        except Exception:
            logger.warning("Stale review reminder failed user_id={}", user.id)


async def stale_review_reminder_loop(bot: Bot, settings: Settings | None = None) -> None:
    settings = settings or get_settings()
    logger.info(
        "Stale review reminder loop started hour_utc={} threshold_hours={}",
        settings.stale_reminder_hour_utc,
        settings.stale_review_hours,
    )
    while True:
        try:
            await send_stale_reminders_once(bot, settings)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Stale review reminder iteration failed")
        await asyncio.sleep(3600)
