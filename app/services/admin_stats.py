from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.start_sources import aggregate_start_sources
from app.db.models import (
    Marketplace,
    MarketplaceAccount,
    Review,
    ReviewStatus,
    Subscription,
    SubscriptionPlan,
    SubscriptionStatus,
    User,
)


async def build_stats_message(session: AsyncSession) -> str:
    users_count = await session.scalar(select(func.count()).select_from(User)) or 0
    reviews_count = await session.scalar(select(func.count()).select_from(Review)) or 0

    active_lite = await session.scalar(
        select(func.count())
        .select_from(Subscription)
        .where(
            Subscription.status == SubscriptionStatus.ACTIVE,
            Subscription.plan == SubscriptionPlan.LITE,
        )
    ) or 0
    active_pro = await session.scalar(
        select(func.count())
        .select_from(Subscription)
        .where(
            Subscription.status == SubscriptionStatus.ACTIVE,
            Subscription.plan == SubscriptionPlan.PRO,
        )
    ) or 0
    pending_qr = await session.scalar(
        select(func.count())
        .select_from(Subscription)
        .where(
            Subscription.status == SubscriptionStatus.PENDING,
        )
    ) or 0

    with_cabinet = await session.scalar(
        select(func.count(func.distinct(MarketplaceAccount.user_id)))
        .select_from(MarketplaceAccount)
        .where(MarketplaceAccount.marketplace.in_((Marketplace.WB, Marketplace.OZON)))
    ) or 0

    replied_users = await session.scalar(
        select(func.count(func.distinct(MarketplaceAccount.user_id)))
        .select_from(Review)
        .join(MarketplaceAccount, Review.account_id == MarketplaceAccount.id)
        .where(Review.status.in_((ReviewStatus.PROCESSED, ReviewStatus.PUBLISHED)))
    ) or 0

    week_ago = datetime.now(UTC) - timedelta(days=7)
    stuck_queue = await session.scalar(
        select(func.count(func.distinct(MarketplaceAccount.user_id)))
        .select_from(Review)
        .join(MarketplaceAccount, Review.account_id == MarketplaceAccount.id)
        .where(
            Review.status == ReviewStatus.NEW,
            Review.created_at <= week_ago,
        )
    ) or 0

    sources = await aggregate_start_sources(session)
    sources_block = ""
    if sources:
        lines = [f"· {name}: <b>{cnt}</b>" for name, cnt in sources]
        sources_block = "\n\n<b>/start источники</b>\n" + "\n".join(lines)

    return (
        "<b>Статистика Голос бренда</b>\n\n"
        f"Пользователей: <b>{users_count}</b>\n"
        f"С кабинетом WB/Ozon: <b>{with_cabinet}</b>\n"
        f"Ответили хотя бы раз: <b>{replied_users}</b>\n"
        f"Очередь &gt;7 дней (юзеров): <b>{stuck_queue}</b>\n\n"
        f"Отзывов в БД: <b>{reviews_count}</b>\n"
        f"Подписки Lite (active): <b>{active_lite}</b>\n"
        f"Подписки PRO (active): <b>{active_pro}</b>\n"
        f"Заявок pending: <b>{pending_qr}</b>"
        f"{sources_block}"
    )
