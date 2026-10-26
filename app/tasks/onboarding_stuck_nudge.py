from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta

from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from loguru import logger
from sqlalchemy import select

from app.core.config import Settings, get_settings
from app.db.models import User
from app.db.session import get_session_factory
from app.bot.utils.proactive_notify import send_proactive
from app.services.onboarding_checklist import onboarding_is_complete


def _keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🚀 Продолжить настройку", callback_data="menu:onboarding")],
            [InlineKeyboardButton(text="🏠 Сводка", callback_data="menu:dashboard")],
        ]
    )


async def onboarding_stuck_nudge_once(bot: Bot, settings: Settings | None = None) -> None:
    settings = settings or get_settings()
    now = datetime.now(UTC)
    cutoff = now - timedelta(hours=24)
    session_factory = get_session_factory()
    sent = 0

    async with session_factory() as session:
        result = await session.execute(
            select(User).where(
                User.terms_accepted_at.isnot(None),
                User.onboarding_completed_at.is_(None),
                User.onboarding_stuck_nudge_at.is_(None),
                User.created_at <= cutoff,
            )
        )
        users = list(result.scalars().all())
        for user in users:
            if await onboarding_is_complete(session, user):
                continue
            try:
                await send_proactive(
                    bot,
                    user.tg_id,
                    "👋 <b>Быстрый старт</b>\n\n"
                    "Вы начали настройку, но ещё не отправили первый ответ на отзыв. "
                    "Это займёт пару минут: кабинет → Sync → тон → ответ.\n\n"
                    "<i>Напоминание одно — дальше не будем докучать.</i>",
                    reply_markup=_keyboard(),
                )
                user.onboarding_stuck_nudge_at = now
                sent += 1
            except Exception as exc:
                logger.warning("onboarding nudge failed tg_id={} err={}", user.tg_id, exc)
        await session.commit()
    if sent:
        logger.info("Onboarding stuck nudges sent: {}", sent)


async def onboarding_stuck_nudge_loop(bot: Bot) -> None:
    settings = get_settings()
    logger.info("Onboarding stuck nudge loop started interval_sec=3600")
    while True:
        try:
            await onboarding_stuck_nudge_once(bot, settings)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            logger.exception("onboarding_stuck_nudge_loop error: {}", exc)
        await asyncio.sleep(3600)
