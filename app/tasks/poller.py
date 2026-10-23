from __future__ import annotations

import asyncio

from datetime import UTC, datetime

from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from loguru import logger

from app.bot.keyboards.empty_states import poller_notify_keyboard
from app.core.config import Settings, get_settings
from app.db.repositories.account import AccountRepository
from app.db.repositories.user import UserRepository
from app.services.marketplace.auto_publish import try_auto_publish_review
from app.services.marketplace.base import MarketplaceAPIError
from app.services.marketplace.sync_service import sync_account_reviews
from app.db.session import get_session_factory

_last_poller_ok_at: datetime | None = None
_last_poller_error: str | None = None


def get_poller_status_line() -> str:
    if _last_poller_ok_at is None:
        return "ожидание первого цикла"
    ts = _last_poller_ok_at.strftime("%d.%m %H:%M")
    if _last_poller_error:
        return f"{ts} UTC · ⚠️ была ошибка"
    return f"{ts} UTC · ✅ OK"


async def poll_marketplace_reviews_once(bot: Bot, settings: Settings | None = None) -> None:
    global _last_poller_ok_at, _last_poller_error
    """Один проход: активные кабинеты → новые отзывы в БД → уведомление селлеру."""
    settings = settings or get_settings()
    session_factory = get_session_factory()
    user_new_counts: dict[int, int] = {}
    user_new_negative: dict[int, int] = {}
    auth_failed_accounts: list[tuple[int, int]] = []

    async with session_factory() as session:
        accounts = await AccountRepository(session).list_active_for_api_sync()

        for account in accounts:
            try:
                created, _, new_reviews = await sync_account_reviews(session, account)
            except MarketplaceAPIError as exc:
                logger.warning("Poller sync failed account_id={} err={}", account.id, exc)
                if exc.status_code == 401:
                    auth_failed_accounts.append((account.user_id, account.id))
                continue

            for review in new_reviews:
                await try_auto_publish_review(session, account=account, review=review, settings=settings)

            if created > 0:
                user_new_counts[account.user_id] = user_new_counts.get(account.user_id, 0) + created
                for review in new_reviews:
                    if review.rating is not None and review.rating <= 3:
                        user_new_negative[account.user_id] = user_new_negative.get(account.user_id, 0) + 1

        await session.commit()

    _last_poller_ok_at = datetime.now(UTC)
    _last_poller_error = None

    for user_id, count in user_new_counts.items():
        async with session_factory() as session:
            user = await UserRepository(session).get_by_id(user_id)
        if user is None:
            continue
        if not user.notify_new_reviews:
            continue
        if user.notify_negative_only:
            count = user_new_negative.get(user_id, 0)
            if count <= 0:
                continue
            notify_text = (
                "✨ <b>ReviewPilot</b>\n"
                f"⚠️ Негативных отзывов (1–3★): <b>{count}</b>\n"
                "<i>Рекомендуем ответить в первую очередь.</i>"
            )
        else:
            notify_text = (
                "✨ <b>ReviewPilot</b>\n"
                f"📬 Новых отзывов: <b>{count}</b>\n"
                "<i>Откройте очередь и ответьте в выбранном тоне.</i>"
            )
        try:
            await bot.send_message(user.tg_id, notify_text, reply_markup=poller_notify_keyboard())
        except Exception:
            logger.warning("Failed to notify user_id={} about new reviews", user_id)

    for user_id, account_id in auth_failed_accounts:
        async with session_factory() as session:
            user = await UserRepository(session).get_by_id(user_id)
        if user is None:
            continue
        try:
            await bot.send_message(
                user.tg_id,
                f"⚠️ Кабинет #{account_id}: API-ключ не принят. "
                "Кабинет отключён — обновите ключ в «Настройках».",
            )
        except Exception:
            logger.warning("Failed to notify user_id={} about auth failure", user_id)


async def marketplace_poller_loop(bot: Bot, settings: Settings | None = None) -> None:
    settings = settings or get_settings()
    interval_sec = max(1, settings.poll_interval_minutes) * 60
    logger.info("Marketplace poller started interval_min={}", settings.poll_interval_minutes)
    while True:
        try:
            await poll_marketplace_reviews_once(bot, settings)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            global _last_poller_error
            _last_poller_error = str(exc)[:200]
            logger.exception("Marketplace poller iteration failed")
        await asyncio.sleep(interval_sec)
