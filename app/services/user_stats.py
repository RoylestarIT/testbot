from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import GeneratedReply, MarketplaceAccount, Review, ReviewStatus


def _start_of_today_utc() -> datetime:
    now = datetime.now(UTC)
    return now.replace(hour=0, minute=0, second=0, microsecond=0)


async def count_replies_today(session: AsyncSession, user_id: int) -> int:
    since = _start_of_today_utc()
    stmt = (
        select(func.count(GeneratedReply.id))
        .select_from(GeneratedReply)
        .join(Review, GeneratedReply.review_id == Review.id)
        .join(MarketplaceAccount, Review.account_id == MarketplaceAccount.id)
        .where(
            MarketplaceAccount.user_id == user_id,
            GeneratedReply.created_at >= since,
        )
    )
    return int((await session.scalar(stmt)) or 0)


async def count_queue_reviews(session: AsyncSession, user_id: int) -> int:
    now = datetime.now(UTC)
    stmt = (
        select(func.count(Review.id))
        .select_from(Review)
        .join(MarketplaceAccount, Review.account_id == MarketplaceAccount.id)
        .where(
            MarketplaceAccount.user_id == user_id,
            Review.status == ReviewStatus.NEW,
            (Review.snoozed_until.is_(None)) | (Review.snoozed_until <= now),
        )
    )
    return int((await session.scalar(stmt)) or 0)


async def avg_rating_new_reviews(session: AsyncSession, user_id: int) -> float | None:
    now = datetime.now(UTC)
    stmt = (
        select(func.avg(Review.rating))
        .select_from(Review)
        .join(MarketplaceAccount, Review.account_id == MarketplaceAccount.id)
        .where(
            MarketplaceAccount.user_id == user_id,
            Review.status == ReviewStatus.NEW,
            Review.rating.isnot(None),
            (Review.snoozed_until.is_(None)) | (Review.snoozed_until <= now),
        )
    )
    value = await session.scalar(stmt)
    if value is None:
        return None
    return round(float(value), 1)


async def build_mini_stats_line(session: AsyncSession, user_id: int) -> str | None:
    today = await count_replies_today(session, user_id)
    queue = await count_queue_reviews(session, user_id)
    avg = await avg_rating_new_reviews(session, user_id)
    avg_part = f" · новые ⭐ <b>{avg}</b>" if avg is not None else ""
    return f"📊 Сегодня ответов: <b>{today}</b> · в очереди: <b>{queue}</b>{avg_part}"


async def build_dashboard_today_line(session: AsyncSession, user_id: int) -> str | None:
    """Только активность за сегодня — без дубля «очереди» (она в статусе сводки)."""
    today = await count_replies_today(session, user_id)
    if today <= 0:
        return None
    return f"📊  Сегодня ответов: <b>{today}</b>"
