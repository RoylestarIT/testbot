from __future__ import annotations

import asyncio

from collections import defaultdict
from datetime import UTC, datetime
from zoneinfo import ZoneInfo

# Время в футере сводки — для селлеров РФ/РБ (совпадает с DIGEST ~9:00 Мinsk)
UI_TIMEZONE = ZoneInfo("Europe/Minsk")

from aiogram import Bot
from loguru import logger

from app.bot.keyboards.empty_states import poller_notify_keyboard
from app.bot.utils.proactive_notify import send_proactive
from app.core.config import Settings, get_settings
from app.db.models import Marketplace
from app.db.repositories.account import AccountRepository
from app.db.repositories.user import UserRepository
from app.services.marketplace.auto_publish import try_auto_publish_review
from app.services.marketplace.base import MarketplaceAPIError
from app.services.marketplace.questions_poll import (
    build_questions_notify,
    format_questions_message,
    refresh_unanswered_questions,
)
from app.services.marketplace.sync_service import sync_account_reviews
from app.services.marketplace.wildberries import WildberriesClient
from app.services.poller_notify import PollerUserNotify, build_poller_notify_text
from app.services.sync_review_notify import apply_review_to_notify_stats, send_new_reviews_notify_if_needed
from app.db.session import get_session_factory

_last_poller_ok_at: datetime | None = None
_last_poller_error: str | None = None


def format_ui_time(when: datetime) -> str:
    if when.tzinfo is None:
        when = when.replace(tzinfo=UTC)
    local = when.astimezone(UI_TIMEZONE)
    return local.strftime("%d.%m %H:%M")


def get_poller_status_line() -> str:
    if _last_poller_ok_at is None:
        return "ожидание первого цикла"
    ts = format_ui_time(_last_poller_ok_at)
    if _last_poller_error:
        return f"{ts} (Минск) · ⚠️ была ошибка"
    return f"{ts} (Минск) · ✅ OK"


def get_poller_health() -> dict[str, object]:
    payload: dict[str, object] = {
        "last_ok_at": _last_poller_ok_at.isoformat() if _last_poller_ok_at else None,
        "last_error": _last_poller_error,
    }
    if _last_poller_ok_at is not None:
        payload["last_ok_minsk"] = format_ui_time(_last_poller_ok_at)
    return payload


async def poll_marketplace_reviews_once(bot: Bot, settings: Settings | None = None) -> None:
    global _last_poller_ok_at, _last_poller_error
    """Один проход: активные кабинеты → новые отзывы в БД → уведомление селлеру."""
    settings = settings or get_settings()
    session_factory = get_session_factory()
    user_stats: dict[int, PollerUserNotify] = defaultdict(PollerUserNotify)
    auth_failed_accounts: list[tuple[int, int]] = []
    question_notifies: dict[int, list] = defaultdict(list)

    async with session_factory() as session:
        accounts = await AccountRepository(session).list_active_for_api_sync()
        wb_client = WildberriesClient() if any(a.marketplace == Marketplace.WB for a in accounts) else None

        for account in accounts:
            try:
                _, _, new_reviews = await sync_account_reviews(session, account)
            except MarketplaceAPIError as exc:
                logger.warning("Poller sync failed account_id={} err={}", account.id, exc)
                if exc.status_code == 401:
                    auth_failed_accounts.append((account.user_id, account.id))
                continue

            stats = user_stats[account.user_id]
            for review in new_reviews:
                outcome = await try_auto_publish_review(
                    session, account=account, review=review, settings=settings
                )
                if outcome.status in ("llm_failed", "api_failed"):
                    min_r = account.auto_publish_min_rating or 4
                    if account.auto_publish_enabled and (
                        review.rating is None or review.rating >= min_r
                    ):
                        stats.auto_failed += 1
                await session.refresh(review)
                apply_review_to_notify_stats(stats, review, outcome)

            if wb_client is not None and account.marketplace == Marketplace.WB:
                try:
                    prev, cur = await refresh_unanswered_questions(
                        session, account, client=wb_client
                    )
                    if cur > prev:
                        question_notifies[account.user_id].append(
                            build_questions_notify(account, delta=cur - prev)
                        )
                except Exception as exc:
                    logger.debug("Questions skip account_id={} err={}", account.id, exc)

        if wb_client is not None:
            await wb_client.aclose()
        await session.commit()

    _last_poller_ok_at = datetime.now(UTC)
    _last_poller_error = None

    if user_stats:
        async with session_factory() as session:
            users = await UserRepository(session).map_by_ids(list(user_stats.keys()))
    else:
        users = {}

    for user_id, stats in user_stats.items():
        user = users.get(user_id)
        if user is None:
            continue
        try:
            await send_new_reviews_notify_if_needed(bot, user, stats)
        except Exception:
            logger.warning("Failed to notify user_id={} about new reviews", user_id)

    for user_id, items in question_notifies.items():
        user = users.get(user_id)
        if user is None:
            async with session_factory() as session:
                user = await UserRepository(session).get_by_id(user_id)
        if user is None or not user.notify_buyer_questions or not items:
            continue
        try:
            await send_proactive(
                bot,
                user.tg_id,
                format_questions_message(items),
                reply_markup=poller_notify_keyboard(),
            )
        except Exception:
            logger.warning("Failed to notify user_id={} about buyer questions", user_id)

    for user_id, account_id in auth_failed_accounts:
        user = users.get(user_id)
        if user is None:
            async with session_factory() as session:
                user = await UserRepository(session).get_by_id(user_id)
        if user is None:
            continue
        try:
            await send_proactive(
                bot,
                user.tg_id,
                f"⚠️ Кабинет #{account_id}: API-ключ не принят. "
                "Кабинет отключён — обновите ключ в «Настройках» → кабинет → «Обновить ключ».",
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
