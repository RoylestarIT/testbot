from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants import MANUAL_SHOP_NAME
from app.db.models import Marketplace, MarketplaceAccount, Review, ReviewStatus, SubscriptionPlan, User
from app.db.repositories.account import AccountRepository
from app.services.generation_limit import remaining_generations_today
from app.services.pro_access import has_paid_pro, is_trial_pro_active
from app.services.plans import (
    FREE_MAX_MARKETPLACE_ACCOUNTS,
    FREE_MAX_TONE_PROFILES,
    count_user_api_accounts,
    count_user_tone_profiles,
    describe_access_tier,
    has_lite_or_higher,
)
from app.services.subscription import get_effective_subscription
from app.services.onboarding_checklist import build_onboarding_checklist
from app.bot.ui import brand_title, footer_hint, kv, muted, section
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
    tier_line = await describe_access_tier(session, user, subscription)
    access_extra: list[str] = []
    if remaining is not None:
        access_extra.append(kv("Генераций сегодня", f"{remaining} / 5"))
    elif subscription and subscription.status.value == "active" and subscription.plan == SubscriptionPlan.LITE:
        access_extra.append(f"  Publish  {muted('копирование')}")
    elif await is_trial_pro_active(user) or (
        subscription and subscription.status.value == "active" and subscription.plan == SubscriptionPlan.PRO
    ):
        access_extra.append(f"  Publish  <b>в API</b>")

    review_lines = [kv("Новые", str(new_count))]
    if snoozed_count:
        review_lines.append(kv("Отложено", str(snoozed_count)))
    review_lines.append(kv("Publish-квота", str(user.free_api_publishes_remaining)))

    if not api_accounts:
        cabinet_block = section("Кабинеты") + f"\n  {muted('Не подключены')}"
    else:
        cab_rows: list[str] = [section("Кабинеты")]
        for acc in api_accounts:
            mp = "WB" if acc.marketplace == Marketplace.WB else "Ozon"
            name = acc.shop_name or f"{mp} #{acc.id}"
            sync = acc.last_sync_at.strftime("%d.%m %H:%M") if acc.last_sync_at else "—"
            dot = "🟢" if acc.is_active else "⚪"
            cab_rows.append(f"  {dot} {name}  ·  {muted(f'sync {sync}')}")
        cabinet_block = "\n".join(cab_rows)

    limits_hint = ""
    if not await has_lite_or_higher(session, user.id):
        acc_n = await count_user_api_accounts(session, user.id)
        tone_n = await count_user_tone_profiles(session, user.id)
        limits_hint = footer_hint(
            f"Free: кабинеты {acc_n}/{FREE_MAX_MARKETPLACE_ACCOUNTS}, "
            f"tone {tone_n}/{FREE_MAX_TONE_PROFILES} · апгрейд в «Подписка»"
        )

    onboarding_hint = ""
    if user.onboarding_completed_at is None and not api_accounts:
        onboarding_hint = f"\n{muted('Подсказка: «Начать настройку» — 3 шага до первого ответа.')}"

    checklist = await build_onboarding_checklist(session, user)
    poller = get_poller_status_line().strip()

    body = (
        brand_title("Сводка", tagline="Ваши отзывы и кабинеты")
        + f"\n{checklist}"
        + section("Доступ")
        + f"\n  {tier_line}"
        + ("\n" + "\n".join(access_extra) if access_extra else "")
        + section("Отзывы")
        + "\n"
        + "\n".join(review_lines)
        + f"\n{cabinet_block}"
        + (f"\n  {muted(poller)}" if poller else "")
        + limits_hint
        + onboarding_hint
    )
    return body
