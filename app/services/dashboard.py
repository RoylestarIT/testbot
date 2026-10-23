from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants import MANUAL_SHOP_NAME
from app.db.models import Marketplace, MarketplaceAccount, Review, ReviewStatus, SubscriptionPlan, User
from app.db.repositories.account import AccountRepository
from app.services.generation_limit import remaining_generations_today
from app.services.pro_access import has_paid_pro, is_trial_pro_active
from app.services.plans import describe_access_tier
from app.services.subscription import get_effective_subscription
from app.tasks.poller import get_poller_status_line


async def build_user_dashboard(session: AsyncSession, user: User) -> str:
    accounts = await AccountRepository(session).list_by_user_id(user.id, active_only=True)
    api_accounts = [
        a
        for a in accounts
        if a.marketplace in (Marketplace.WB, Marketplace.OZON)
        and (a.shop_name is None or a.shop_name != MANUAL_SHOP_NAME)
    ]

    now = datetime.now(UTC)
    new_reviews_stmt = (
        select(func.count(Review.id))
        .select_from(Review)
        .join(MarketplaceAccount, Review.account_id == MarketplaceAccount.id)
        .where(
            MarketplaceAccount.user_id == user.id,
            Review.status == ReviewStatus.NEW,
            (Review.snoozed_until.is_(None)) | (Review.snoozed_until <= now),
        )
    )
    new_count = int((await session.scalar(new_reviews_stmt)) or 0)

    snoozed_stmt = (
        select(func.count(Review.id))
        .select_from(Review)
        .join(MarketplaceAccount, Review.account_id == MarketplaceAccount.id)
        .where(
            MarketplaceAccount.user_id == user.id,
            Review.status == ReviewStatus.NEW,
            Review.snoozed_until.isnot(None),
            Review.snoozed_until > now,
        )
    )
    snoozed_count = int((await session.scalar(snoozed_stmt)) or 0)

    subscription = await get_effective_subscription(session, user.id)
    remaining = await remaining_generations_today(session, user.id)
    plan_line = await describe_access_tier(session, user, subscription)
    if remaining is not None:
        plan_line += f"\nГенераций сегодня: <b>{remaining}</b> / 5"
    elif (
        subscription
        and subscription.status.value == "active"
        and subscription.plan == SubscriptionPlan.LITE
    ):
        plan_line += "\nPublish в API: <b>нет</b> (только копирование)"
    elif await is_trial_pro_active(user) or (
        subscription
        and subscription.status.value == "active"
        and subscription.plan == SubscriptionPlan.PRO
    ):
        plan_line += "\nPublish в API: <b>да</b>"

    if not api_accounts:
        cabinets = "⚠️ Кабинеты WB/Ozon: <b>не подключены</b>"
    else:
        parts: list[str] = []
        for acc in api_accounts:
            mp = "WB" if acc.marketplace == Marketplace.WB else "Ozon"
            name = acc.shop_name or f"{mp} #{acc.id}"
            sync = (
                acc.last_sync_at.strftime("%d.%m %H:%M")
                if acc.last_sync_at
                else "ещё не было"
            )
            st = "✅" if acc.is_active else "⏸"
            parts.append(f"{st} {name} · sync {sync} UTC")
        cabinets = "🏪 Кабинеты:\n" + "\n".join(f"  • {p}" for p in parts)

    onboarding_hint = ""
    if user.onboarding_completed_at is None and not api_accounts:
        onboarding_hint = "\n\n👉 Нажмите <b>«Начать настройку»</b> — проведём за 3 шага."

    return (
        "🏠 <b>Сводка</b>\n\n"
        f"{plan_line}\n"
        f"📬 Новых отзывов: <b>{new_count}</b>"
        + (f" · отложено: {snoozed_count}" if snoozed_count else "")
        + "\n"
        f"🎟 Бесплатных publish в API: <b>{user.free_api_publishes_remaining}</b>\n"
        f"{cabinets}\n"
        f"{get_poller_status_line()}"
        f"{onboarding_hint}"
    )
