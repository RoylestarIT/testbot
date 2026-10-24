from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import GeneratedReply, MarketplaceAccount, Review, ReviewStatus


def _since_days(days: int) -> datetime:
    return datetime.now(UTC) - timedelta(days=days)


async def count_distinct_reviews_with_generation(
    session: AsyncSession, user_id: int, *, days: int
) -> int:
    since = _since_days(days)
    stmt = (
        select(func.count(func.distinct(Review.id)))
        .select_from(GeneratedReply)
        .join(Review, GeneratedReply.review_id == Review.id)
        .join(MarketplaceAccount, Review.account_id == MarketplaceAccount.id)
        .where(
            MarketplaceAccount.user_id == user_id,
            GeneratedReply.created_at >= since,
        )
    )
    return int((await session.scalar(stmt)) or 0)


async def count_closed_with_activity_in_period(
    session: AsyncSession, user_id: int, *, days: int
) -> int:
    """Отзывы со статусом processed/published, по которым была активность за период."""
    since = _since_days(days)
    stmt = (
        select(func.count(func.distinct(Review.id)))
        .select_from(GeneratedReply)
        .join(Review, GeneratedReply.review_id == Review.id)
        .join(MarketplaceAccount, Review.account_id == MarketplaceAccount.id)
        .where(
            MarketplaceAccount.user_id == user_id,
            GeneratedReply.created_at >= since,
            Review.status.in_((ReviewStatus.PROCESSED, ReviewStatus.PUBLISHED)),
        )
    )
    return int((await session.scalar(stmt)) or 0)


async def queue_negative_share(session: AsyncSession, user_id: int) -> tuple[int, int]:
    """(негатив ≤3★ в очереди, всего в очереди)."""
    now = datetime.now(UTC)
    queue_filters = (
        MarketplaceAccount.user_id == user_id,
        Review.status == ReviewStatus.NEW,
        (Review.snoozed_until.is_(None)) | (Review.snoozed_until <= now),
    )
    total_stmt = (
        select(func.count(Review.id))
        .select_from(Review)
        .join(MarketplaceAccount, Review.account_id == MarketplaceAccount.id)
        .where(*queue_filters)
    )
    total = int((await session.scalar(total_stmt)) or 0)
    if total == 0:
        return 0, 0
    low_stmt = (
        select(func.count(Review.id))
        .select_from(Review)
        .join(MarketplaceAccount, Review.account_id == MarketplaceAccount.id)
        .where(*queue_filters, Review.rating.isnot(None), Review.rating <= 3)
    )
    low = int((await session.scalar(low_stmt)) or 0)
    return low, total


async def count_reviews_by_status(session: AsyncSession, user_id: int, status: ReviewStatus, *, days: int) -> int:
    since = _since_days(days)
    stmt = (
        select(func.count(Review.id))
        .select_from(Review)
        .join(MarketplaceAccount, Review.account_id == MarketplaceAccount.id)
        .join(GeneratedReply, GeneratedReply.review_id == Review.id)
        .where(
            MarketplaceAccount.user_id == user_id,
            Review.status == status,
            GeneratedReply.created_at >= since,
        )
    )
    return int((await session.scalar(stmt)) or 0)


async def build_publish_activity_line(session: AsyncSession, user_id: int, *, days: int = 7) -> str | None:
    published = await count_reviews_by_status(session, user_id, ReviewStatus.PUBLISHED, days=days)
    copied = await count_reviews_by_status(session, user_id, ReviewStatus.PROCESSED, days=days)
    if published + copied == 0:
        return None
    return (
        f"📤  За {days} дн.: publish в API <b>{published}</b> · "
        f"вручную/копия <b>{copied}</b>"
    )


async def build_period_analytics_block(session: AsyncSession, user_id: int) -> str:
    from app.services.user_stats import avg_rating_new_reviews

    w7_gen = await count_distinct_reviews_with_generation(session, user_id, days=7)
    w7_closed = await count_closed_with_activity_in_period(session, user_id, days=7)
    w30_gen = await count_distinct_reviews_with_generation(session, user_id, days=30)
    low, queue = await queue_negative_share(session, user_id)
    avg = await avg_rating_new_reviews(session, user_id)

    pub7 = await count_reviews_by_status(session, user_id, ReviewStatus.PUBLISHED, days=7)
    copy7 = await count_reviews_by_status(session, user_id, ReviewStatus.PROCESSED, days=7)

    lines = ["<b>📈 Активность</b>"]
    lines.append(
        f"· 7 дней: генерации по <b>{w7_gen}</b> отзывам · закрыто <b>{w7_closed}</b>"
    )
    if pub7 or copy7:
        lines.append(f"· Publish в API: <b>{pub7}</b> · копия/ручная отправка: <b>{copy7}</b>")
    lines.append(f"· 30 дней: генерации по <b>{w30_gen}</b> отзывам")
    if queue:
        pct = round(100 * low / queue) if queue else 0
        avg_s = f" · средняя ⭐ <b>{avg}</b>" if avg is not None else ""
        lines.append(f"· Очередь: <b>{queue}</b> · негатив ≤3★: <b>{low}</b> ({pct}%){avg_s}")
    else:
        lines.append("· Очередь пуста")
    return "\n".join(lines)
