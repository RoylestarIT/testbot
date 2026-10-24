from __future__ import annotations

import asyncio
from collections import defaultdict
from datetime import UTC, datetime
from zoneinfo import ZoneInfo

from aiogram import Bot
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards.empty_states import poller_notify_keyboard
from app.core.config import Settings, get_settings
from app.db.models import Marketplace, MarketplaceAccount, ReviewStatus
from app.db.repositories.account import AccountRepository
from app.db.repositories.user import UserRepository
from app.db.session import get_session_factory
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

# Время в футере сводки — для селлеров РФ/РБ (совпадает с DIGEST ~9:00 Минск)
UI_TIMEZONE = ZoneInfo("Europe/Minsk")

_last_poller_ok_at: datetime | None = None
_last_poller_error: str | None = None
_last_failed_accounts: int = 0


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
        return f"sync {ts} (Минск) · ⚠️ была ошибка"
    return f"sync {ts} (Минск) · ✅ OK"


def get_poller_health() -> dict[str, object]:
    payload: dict[str, object] = {
        "last_ok_at": _last_poller_ok_at.isoformat() if _last_poller_ok_at else None,
        "last_error": _last_poller_error,
        "failed_accounts_last_run": _last_failed_accounts,
    }
    if _last_poller_ok_at is not None:
        payload["last_ok_minsk"] = format_ui_time(_last_poller_ok_at)
    return payload


async def _sync_one_account(
    session: AsyncSession,
    account: MarketplaceAccount,
    *,
    settings: Settings,
    wb_client: WildberriesClient | None,
    stats: PollerUserNotify,
    question_notifies: dict[int, list],
) -> None:
    _, _, new_reviews = await sync_account_reviews(session, account)
    await session.commit()

    for review in new_reviews:
        outcome = await try_auto_publish_review(
            session, account=account, review=review, settings=settings
        )
        # Publishing already happened in the marketplace — persist it before the next review.
        await session.commit()
        if outcome.status == "published":
            stats.auto_published += 1
            if outcome.reply_preview:
                stats.auto_previews.append(outcome.reply_preview)
        elif outcome.status in ("llm_failed", "api_failed"):
            min_r = account.auto_publish_min_rating or 4
            if account.auto_publish_enabled and (review.rating is None or review.rating >= min_r):
                stats.auto_failed += 1
        await session.refresh(review)
        if review.status == ReviewStatus.NEW:
            stats.queue_new += 1
            if review.rating is not None and review.rating <= 3:
                stats.queue_negative += 1

    if wb_client is not None and account.marketplace == Marketplace.WB:
        try:
            prev, cur = await refresh_unanswered_questions(session, account, client=wb_client)
            if cur > prev:
                question_notifies[account.user_id].append(
                    build_questions_notify(account, delta=cur - prev)
                )
        except Exception as exc:
            logger.debug("Questions skip account_id={} err={}", account.id, exc)
        await session.commit()


async def _record_account_error(session_factory, account_id: int, message: str) -> None:
    async with session_factory() as session:
        account = await AccountRepository(session).get_by_id(account_id)
        if account is not None:
            account.last_sync_error = message[:500]
            await session.commit()


async def poll_marketplace_reviews_once(bot: Bot, settings: Settings | None = None) -> None:
    """Один проход: активные кабинеты → новые отзывы в БД → уведомление селлеру.

    Каждый кабинет — в своей сессии: сбой одного (таймаут, ошибка LLM) не мешает остальным
    и не откатывает уже опубликованные ответы.
    """
    global _last_poller_ok_at, _last_poller_error, _last_failed_accounts
    settings = settings or get_settings()
    session_factory = get_session_factory()
    user_stats: dict[int, PollerUserNotify] = defaultdict(PollerUserNotify)
    auth_failed_accounts: list[tuple[int, int]] = []
    question_notifies: dict[int, list] = defaultdict(list)
    failed_accounts = 0

    async with session_factory() as session:
        accounts = await AccountRepository(session).list_active_for_api_sync()
        targets = [(a.id, a.user_id, a.marketplace) for a in accounts]

    wb_client = WildberriesClient() if any(m == Marketplace.WB for _, _, m in targets) else None
    try:
        for account_id, user_id, _marketplace in targets:
            try:
                async with session_factory() as session:
                    account = await AccountRepository(session).get_by_id(account_id)
                    if account is None or not account.is_active:
                        continue
                    try:
                        await _sync_one_account(
                            session,
                            account,
                            settings=settings,
                            wb_client=wb_client,
                            stats=user_stats[user_id],
                            question_notifies=question_notifies,
                        )
                    except MarketplaceAPIError as exc:
                        # sync_account_reviews flushed last_sync_error / deactivation on 401.
                        await session.commit()
                        logger.warning("Poller sync failed account_id={} err={}", account_id, exc)
                        if exc.status_code == 401:
                            auth_failed_accounts.append((user_id, account_id))
            except Exception as exc:
                failed_accounts += 1
                logger.exception("Poller account failed account_id={}", account_id)
                await _record_account_error(
                    session_factory, account_id, f"Временная ошибка синхронизации: {exc}"
                )
    finally:
        if wb_client is not None:
            await wb_client.aclose()

    _last_poller_ok_at = datetime.now(UTC)
    _last_poller_error = None
    _last_failed_accounts = failed_accounts

    if user_stats:
        async with session_factory() as session:
            users = await UserRepository(session).map_by_ids(list(user_stats.keys()))
    else:
        users = {}

    for user_id, stats in user_stats.items():
        user = users.get(user_id)
        if user is None or not user.notify_new_reviews:
            continue
        notify_text = build_poller_notify_text(
            stats=stats,
            negative_only=user.notify_negative_only,
        )
        if notify_text is None:
            continue
        try:
            await bot.send_message(user.tg_id, notify_text, reply_markup=poller_notify_keyboard())
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
            await bot.send_message(
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
            await bot.send_message(
                user.tg_id,
                f"⚠️ Кабинет #{account_id}: API-ключ не принят. "
                "Кабинет отключён — обновите ключ в «Настройках» → кабинет → «Обновить ключ».",
            )
        except Exception:
            logger.warning("Failed to notify user_id={} about auth failure", user_id)


async def marketplace_poller_loop(bot: Bot, settings: Settings | None = None) -> None:
    global _last_poller_error
    settings = settings or get_settings()
    interval_sec = max(1, settings.poll_interval_minutes) * 60
    logger.info("Marketplace poller started interval_min={}", settings.poll_interval_minutes)
    while True:
        try:
            await poll_marketplace_reviews_once(bot, settings)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            _last_poller_error = str(exc)[:200]
            logger.exception("Marketplace poller iteration failed")
        await asyncio.sleep(interval_sec)
