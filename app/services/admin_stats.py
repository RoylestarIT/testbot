from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Review, Subscription, SubscriptionPlan, SubscriptionStatus, User


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

    return (
        "<b>Статистика ReviewPilot</b>\n\n"
        f"Пользователей: <b>{users_count}</b>\n"
        f"Отзывов в БД: <b>{reviews_count}</b>\n"
        f"Подписки Lite (active): <b>{active_lite}</b>\n"
        f"Подписки PRO (active): <b>{active_pro}</b>\n"
        f"Заявок pending: <b>{pending_qr}</b>"
    )
