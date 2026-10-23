from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.copy import DIFFERENTIATORS_DASHBOARD_LINE
from app.bot.ui import dashboard_home, muted
from app.constants import MANUAL_SHOP_NAME
from app.db.models import Marketplace, MarketplaceAccount, Review, ReviewStatus, SubscriptionPlan, User
from app.db.repositories.account import AccountRepository
from app.services.generation_limit import remaining_generations_today
from app.services.plans import (
    FREE_MAX_MARKETPLACE_ACCOUNTS,
    FREE_MAX_TONE_PROFILES,
    count_user_api_accounts,
    count_user_tone_profiles,
    describe_access_tier,
    has_lite_or_higher,
)
from app.services.subscription import get_effective_subscription
from app.services.onboarding_checklist import build_onboarding_nudge
from app.services.user_stats import build_mini_stats_line
from app.tasks.poller import get_poller_status_line


def _review_word(n: int) -> str:
    n = abs(n) % 100
    n1 = n % 10
    if 11 <= n <= 19:
        return "отзывов"
    if n1 == 1:
        return "отзыв"
    if 2 <= n1 <= 4:
        return "отзыва"
    return "отзывов"


async def build_user_dashboard(session: AsyncSession, user: User) -> str:
    accounts = await AccountRepository(session).list_by_user_id(user.id, active_only=True)
    api_accounts = [
        a
        for a in accounts
        if a.marketplace in (Marketplace.WB, Marketplace.OZON)
        and (a.shop_name is None or a.shop_name != MANUAL_SHOP_NAME)
    ]

    now = datetime.now(UTC)
    new_count = int(
        (
            await session.scalar(
                select(func.count(Review.id))
                .select_from(Review)
                .join(MarketplaceAccount, Review.account_id == MarketplaceAccount.id)
                .where(
                    MarketplaceAccount.user_id == user.id,
                    Review.status == ReviewStatus.NEW,
                    (Review.snoozed_until.is_(None)) | (Review.snoozed_until <= now),
                )
            )
        )
        or 0
    )
    snoozed_count = int(
        (
            await session.scalar(
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
        )
        or 0
    )

    subscription = await get_effective_subscription(session, user.id)
    remaining = await remaining_generations_today(session, user.id)
    tier = await describe_access_tier(session, user, subscription)

    if subscription and subscription.status.value == "active":
        tier_icon = "💎" if subscription.plan == SubscriptionPlan.PRO else "✨"
    elif user.trial_pro_until:
        tier_icon = "🎁"
    else:
        tier_icon = "🆓"

    if new_count > 0:
        focus = f"📬  <b>{new_count}</b> {_review_word(new_count)} ждёт ответа"
        hint = "👇 Кнопка «Очередь отзывов»"
    else:
        focus = "📭  Новых отзывов нет"
        hint = "🔄 Нажмите «Sync» на сводке"

    mini = await build_mini_stats_line(session, user.id)
    details: list[str] = []
    if mini:
        details.append(mini)
        details.append("")
    details.append(f"{tier_icon}  Тариф: <b>{tier}</b>")

    if remaining is not None:
        details.append(f"⚡  Генераций сегодня: <b>{remaining}</b> / 5")
    elif subscription and subscription.status.value == "active" and subscription.plan == SubscriptionPlan.LITE:
        details.append("📋  Publish: копирование в кабинет")
    else:
        details.append(f"🚀  Publish в API: квота <b>{user.free_api_publishes_remaining}</b>")

    if snoozed_count:
        details.append(f"⏳  Отложено: <b>{snoozed_count}</b>")

    if api_accounts:
        names = []
        for acc in api_accounts[:3]:
            mp = "🟣" if acc.marketplace == Marketplace.WB else "🔵"
            label = acc.shop_name or ("WB" if acc.marketplace == Marketplace.WB else "Ozon")
            names.append(f"{mp} {label}")
        tail = f" (+{len(api_accounts) - 3})" if len(api_accounts) > 3 else ""
        details.append(f"🏪  {', '.join(names)}{tail}")
    else:
        details.append("🏪  Кабинеты: <b>не подключены</b>")

    nudge = await build_onboarding_nudge(session, user)
    if nudge:
        details.append("")
        details.append(nudge)

    if not await has_lite_or_higher(session, user.id):
        acc_n = await count_user_api_accounts(session, user.id)
        tone_n = await count_user_tone_profiles(session, user.id)
        details.append(
            muted(
                f"🔒 Free: {acc_n}/{FREE_MAX_MARKETPLACE_ACCOUNTS} каб., "
                f"{tone_n}/{FREE_MAX_TONE_PROFILES} tone"
            )
        )

    details.append("")
    details.append(DIFFERENTIATORS_DASHBOARD_LINE)

    footer_raw = get_poller_status_line().strip()
    footer = f"🔄 {footer_raw}" if footer_raw else None

    return dashboard_home(
        focus_line=focus,
        focus_hint=hint,
        detail_lines=details,
        footer=footer,
    )
