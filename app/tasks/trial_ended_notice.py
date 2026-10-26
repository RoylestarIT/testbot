from __future__ import annotations

import asyncio
from datetime import UTC, datetime

from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from loguru import logger
from sqlalchemy import select

from app.core.config import Settings, get_settings
from app.db.models import User
from app.db.session import get_session_factory
from app.bot.utils.proactive_notify import send_proactive
from app.services.access_messaging import trial_ended_screen_text
from app.services.pro_access import has_paid_pro, is_trial_pro_active


def _keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✓ Понятно", callback_data="menu:trial_ended:ack")],
            [InlineKeyboardButton(text="💎 Подписка", callback_data="menu:subscription")],
        ]
    )


async def trial_ended_notice_once(bot: Bot, settings: Settings | None = None) -> None:
    settings = settings or get_settings()
    now = datetime.now(UTC)
    session_factory = get_session_factory()
    sent = 0

    async with session_factory() as session:
        result = await session.execute(
            select(User).where(
                User.trial_pro_used.is_(True),
                User.trial_pro_until.isnot(None),
                User.trial_pro_until < now,
                User.trial_ended_notice_at.is_(None),
            )
        )
        for user in result.scalars().all():
            if await is_trial_pro_active(user):
                continue
            if await has_paid_pro(session, user.id):
                user.trial_ended_notice_at = now
                continue
            try:
                await send_proactive(
                    bot,
                    user.tg_id,
                    trial_ended_screen_text(user),
                    reply_markup=_keyboard(),
                )
                user.trial_ended_notice_at = now
                sent += 1
            except Exception as exc:
                logger.warning("trial ended notice failed tg_id={} err={}", user.tg_id, exc)
        await session.commit()
    if sent:
        logger.info("Trial ended notices sent: {}", sent)


async def trial_ended_notice_loop(bot: Bot) -> None:
    settings = get_settings()
    logger.info("Trial ended notice loop started interval_sec=3600")
    while True:
        try:
            await trial_ended_notice_once(bot, settings)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            logger.exception("trial_ended_notice_loop error: {}", exc)
        await asyncio.sleep(3600)
