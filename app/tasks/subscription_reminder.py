from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta

from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from loguru import logger
from sqlalchemy import select

from app.core.config import Settings, get_settings
from app.db.models import Subscription, SubscriptionStatus, User
from app.db.session import get_session_factory
from app.services.subscription import plan_label


def _renewal_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="💳 Оплатить", callback_data="sub:pay:menu"),
                InlineKeyboardButton(text="🧮 Калькулятор", callback_data="sub:calc"),
            ],
            [InlineKeyboardButton(text="💎 Подписка", callback_data="menu:subscription")],
        ]
    )


async def subscription_reminder_once(bot: Bot, settings: Settings | None = None) -> None:
    settings = settings or get_settings()
    now = datetime.now(UTC)
    window_end = now + timedelta(days=3)
    session_factory = get_session_factory()

    async with session_factory() as session:
        result = await session.execute(
            select(Subscription, User)
            .join(User, Subscription.user_id == User.id)
            .where(
                Subscription.status == SubscriptionStatus.ACTIVE,
                Subscription.expires_at.isnot(None),
                Subscription.expires_at > now,
                Subscription.expires_at <= window_end,
            )
        )
        rows = result.all()

        for subscription, user in rows:
            if subscription.expires_at is None:
                continue
            if user.last_subscription_reminder_at and user.last_subscription_reminder_at.date() == now.date():
                continue
            days_left = (subscription.expires_at.date() - now.date()).days
            if days_left not in (1, 2, 3):
                continue
            text = (
                f"⏳ Подписка <b>{plan_label(subscription.plan)}</b> заканчивается через "
                f"<b>{days_left}</b> дн. (до {subscription.expires_at.strftime('%d.%m.%Y')}).\n"
                "Продлите сейчас — PRO publish и лимиты сохранятся без паузы.\n"
                "<i>Не уверены в тарифе? Откройте «Калькулятор» ниже.</i>"
            )
            try:
                await bot.send_message(user.tg_id, text, reply_markup=_renewal_keyboard())
                user.last_subscription_reminder_at = now
            except Exception:
                logger.warning("subscription reminder failed user_id={}", user.id)
        await session.commit()

    async with session_factory() as session:
        expired_result = await session.execute(
            select(Subscription, User)
            .join(User, Subscription.user_id == User.id)
            .where(
                Subscription.status == SubscriptionStatus.ACTIVE,
                Subscription.expires_at.isnot(None),
                Subscription.expires_at <= now,
            )
        )
        for subscription, user in expired_result.all():
            subscription.status = SubscriptionStatus.EXPIRED
            try:
                await bot.send_message(
                    user.tg_id,
                    "📭 Подписка закончилась — вы на <b>Free</b> "
                    "(5 генераций/день, 1 кабинет, ответы вручную в кабинете).\n"
                    "<i>🧮 Калькулятор — подобрать Lite или PRO под ваш объём.</i>",
                    reply_markup=_renewal_keyboard(),
                )
            except Exception:
                pass
        await session.commit()


async def subscription_reminder_loop(bot: Bot, settings: Settings | None = None) -> None:
    settings = settings or get_settings()
    interval = max(3600, settings.poll_interval_minutes * 60)
    logger.info("Subscription reminder loop started interval_sec={}", interval)
    while True:
        try:
            await subscription_reminder_once(bot, settings)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("subscription reminder iteration failed")
        await asyncio.sleep(interval)
