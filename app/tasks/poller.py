from __future__ import annotations

import asyncio

from aiogram import Bot
from loguru import logger

from app.core.config import Settings, get_settings
from app.db.repositories.account import AccountRepository
from app.db.repositories.user import UserRepository
from app.services.marketplace.base import MarketplaceAPIError
from app.services.marketplace.sync_service import sync_account_reviews
from app.db.session import get_session_factory


async def poll_marketplace_reviews_once(bot: Bot, settings: Settings | None = None) -> None:
    """Один проход: активные кабинеты → новые отзывы в БД → уведомление селлеру."""
    settings = settings or get_settings()
    session_factory = get_session_factory()
    async with session_factory() as session:
        accounts = await AccountRepository(session).list_active_all()
        user_new_counts: dict[int, int] = {}

        for account in accounts:
            try:
                created, _ = await sync_account_reviews(session, account)
            except MarketplaceAPIError as exc:
                logger.warning("Poller sync failed account_id={} err={}", account.id, exc)
                continue
            if created > 0:
                user_new_counts[account.user_id] = user_new_counts.get(account.user_id, 0) + created

        await session.commit()

    for user_id, count in user_new_counts.items():
        async with session_factory() as session:
            user = await UserRepository(session).get_by_id(user_id)
        if user is None:
            continue
        try:
            await bot.send_message(
                user.tg_id,
                f"📩 ReviewPilot: новых отзывов — <b>{count}</b>.\n"
                "Откройте «Отзывы → Новые из маркетплейсов».",
            )
        except Exception:
            logger.warning("Failed to notify user_id={} about new reviews", user_id)


async def marketplace_poller_loop(bot: Bot, settings: Settings | None = None) -> None:
    settings = settings or get_settings()
    interval_sec = max(1, settings.poll_interval_minutes) * 60
    logger.info("Marketplace poller started interval_min={}", settings.poll_interval_minutes)
    while True:
        try:
            await poll_marketplace_reviews_once(bot, settings)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Marketplace poller iteration failed")
        await asyncio.sleep(interval_sec)
