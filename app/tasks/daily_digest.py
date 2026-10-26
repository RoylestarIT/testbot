from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta

from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from loguru import logger
from sqlalchemy import func, select

from app.core.config import Settings, get_settings
from app.db.models import MarketplaceAccount, Review, ReviewStatus, User
from app.db.repositories.user import UserRepository
from app.db.session import get_session_factory
from app.bot.ui import BRAND, ICON, REVIEWS_HUB_BUTTON
from app.bot.utils.proactive_notify import send_proactive
from app.services.subscription import get_effective_subscription, plan_label


def _digest_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=REVIEWS_HUB_BUTTON, callback_data="review:mp:list")],
            [InlineKeyboardButton(text="🏠 Сводка", callback_data="menu:dashboard")],
        ]
    )


async def build_digest_text(session, user: User) -> str:
    now = datetime.now(UTC)
    new_count = int(
        (
            await session.scalar(
                select(func.count(Review.id))
                .select_from(Review)
                .join(MarketplaceAccount, Review.account_id == MarketplaceAccount.id)
                .where(
                    MarketplaceAccount.user_id == user.id,
                    Review.status == ReviewStatus.NEW,
                    (Review.snoozed_until.is_(None)) | (Review.snoozed_until <= now),
                )
            )
        )
        or 0
    )
    negative = int(
        (
            await session.scalar(
                select(func.count(Review.id))
                .select_from(Review)
                .join(MarketplaceAccount, Review.account_id == MarketplaceAccount.id)
                .where(
                    MarketplaceAccount.user_id == user.id,
                    Review.status == ReviewStatus.NEW,
                    Review.rating.isnot(None),
                    Review.rating <= 3,
                    (Review.snoozed_until.is_(None)) | (Review.snoozed_until <= now),
                )
            )
        )
        or 0
    )
    subscription = await get_effective_subscription(session, user.id)
    sub_line = "Free"
    if subscription is not None:
        sub_line = plan_label(subscription.plan)
    if subscription and subscription.expires_at:
        days_left = (subscription.expires_at - now).days
        if 0 <= days_left <= 7:
            sub_line += f" · истекает через {days_left} д."

    lines = [
        f"{ICON} <b>{BRAND}</b> · утренний дайджест",
        "",
        f"📬 Новых в очереди: <b>{new_count}</b>",
    ]
    if negative:
        lines.append(f"⚠️ Негатив 1–3★: <b>{negative}</b>")
    lines.append(f"💎 Тариф: <b>{sub_line}</b>")
    lines.append("")
    lines.append("<i>Хорошего дня и быстрых ответов покупателям.</i>")
    return "\n".join(lines)


async def send_digests_once(bot: Bot, settings: Settings | None = None) -> None:
    settings = settings or get_settings()
    now = datetime.now(UTC)
    if now.hour != settings.digest_hour_utc:
        return

    session_factory = get_session_factory()
    async with session_factory() as session:
        result = await session.execute(select(User).where(User.notify_daily_digest.is_(True)))
        users = list(result.scalars().all())

    for user in users:
        if user.last_daily_digest_at and user.last_daily_digest_at.date() == now.date():
            continue
        async with session_factory() as session:
            db_user = await UserRepository(session).get_by_id(user.id)
            if db_user is None:
                continue
            text = await build_digest_text(session, db_user)
            db_user.last_daily_digest_at = now
            await session.commit()
        try:
            await send_proactive(bot, user.tg_id, text, reply_markup=_digest_keyboard())
        except Exception:
            logger.warning("Daily digest failed for user_id={}", user.id)


async def daily_digest_loop(bot: Bot, settings: Settings | None = None) -> None:
    settings = settings or get_settings()
    logger.info("Daily digest loop started hour_utc={}", settings.digest_hour_utc)
    while True:
        try:
            await send_digests_once(bot, settings)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Daily digest iteration failed")
        await asyncio.sleep(3600)
