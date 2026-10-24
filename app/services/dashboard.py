from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.ui import REVIEWS_HUB_BUTTON, dashboard_home, muted, quote
from app.core.config import get_settings
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
from app.bot.product_news import build_product_news_banner, user_should_see_product_news
from app.services.onboarding_checklist import build_onboarding_checklist_block, build_onboarding_nudge
from app.services.period_analytics import build_publish_activity_line
from app.services.user_stats import avg_rating_new_reviews, build_dashboard_today_line
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


def _status_block(
    *,
    new_count: int,
    snoozed_count: int,
    has_cabinets: bool,
) -> str:
    if new_count > 0:
        head = f"📬  <b>{new_count}</b> {_review_word(new_count)} ждёт ответа"
        if snoozed_count:
            head += f"  ·  ⏳ отложено <b>{snoozed_count}</b>"
        tail = muted(f"→ {REVIEWS_HUB_BUTTON}")
    elif snoozed_count:
        head = f"📭  В активной очереди пусто  ·  ⏳ отложено <b>{snoozed_count}</b>"
        tail = muted(f"→ {REVIEWS_HUB_BUTTON}")
    else:
        head = "📭  Новых отзывов нет"
        if has_cabinets:
            tail = muted("→ 🔄 Sync, если нужно подтянуть сейчас")
        else:
            tail = muted("→ ⚙️ Настройки: подключите WB или Ozon")
    return quote(f"{head}\n{tail}")


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

    poll_min = get_settings().poll_interval_minutes
    has_cabinets = bool(api_accounts)

    status = _status_block(
        new_count=new_count,
        snoozed_count=snoozed_count,
        has_cabinets=has_cabinets,
    )

    meta: list[str] = [f"{tier_icon}  {tier}"]

    if remaining is not None:
        meta.append(f"⚡  Генераций сегодня: <b>{remaining}</b> / 5")
    elif subscription and subscription.status.value == "active" and subscription.plan == SubscriptionPlan.LITE:
        meta.append("📋  Ответы — копированием в кабинет")
    elif user.trial_pro_until or (
        subscription and subscription.status.value == "active" and subscription.plan == SubscriptionPlan.PRO
    ):
        meta.append(f"🚀  Publish-квота: <b>{user.free_api_publishes_remaining}</b>")
    elif user.free_api_publishes_remaining:
        meta.append(f"🚀  Пробных publish: <b>{user.free_api_publishes_remaining}</b>")

    if has_cabinets:
        names = []
        for acc in api_accounts[:2]:
            mp = "🟣" if acc.marketplace == Marketplace.WB else "🔵"
            label = acc.shop_name or ("WB" if acc.marketplace == Marketplace.WB else "Ozon")
            names.append(f"{mp} {label}")
        tail = f" +{len(api_accounts) - 2}" if len(api_accounts) > 2 else ""
        meta.append(f"🏪  {', '.join(names)}{tail}")
    else:
        meta.append("🏪  Кабинеты не подключены")

    today_line = await build_dashboard_today_line(session, user.id)
    if today_line:
        meta.append(today_line)

    publish_line = await build_publish_activity_line(session, user.id, days=7)
    if publish_line:
        meta.append(publish_line)

    if new_count > 0:
        avg = await avg_rating_new_reviews(session, user.id)
        if avg is not None:
            meta.append(f"⭐  Средняя оценка в очереди: <b>{avg}</b>")

    settings = get_settings()
    show_product_news = user_should_see_product_news(user, settings)
    checklist = await build_onboarding_checklist_block(session, user)
    nudge = await build_onboarding_nudge(session, user)
    if checklist:
        nudge = f"{checklist}\n\n{nudge}" if nudge else checklist
    if show_product_news:
        nudge_line = build_product_news_banner(settings)
        if nudge:
            nudge_line = f"{nudge_line}\n\n{muted(nudge)}"
    elif nudge:
        nudge_line = muted(nudge)
    else:
        nudge_line = None

    if not await has_lite_or_higher(session, user.id):
        acc_n = await count_user_api_accounts(session, user.id)
        tone_n = await count_user_tone_profiles(session, user.id)
        if nudge_line:
            nudge_line = (
                nudge_line
                + "\n"
                + muted(
                    f"🔒 Free: {acc_n}/{FREE_MAX_MARKETPLACE_ACCOUNTS} каб., "
                    f"{tone_n}/{FREE_MAX_TONE_PROFILES} тон"
                )
            )
        else:
            nudge_line = muted(
                f"🔒 Free: {acc_n}/{FREE_MAX_MARKETPLACE_ACCOUNTS} каб., "
                f"{tone_n}/{FREE_MAX_TONE_PROFILES} тон"
            )

    footer_parts: list[str] = []
    if has_cabinets:
        footer_parts.append(f"авто-sync каждые {poll_min} мин")
    poller = get_poller_status_line().strip()
    if poller:
        footer_parts.append(poller)
    footer = " · ".join(footer_parts) if footer_parts else None

    return dashboard_home(
        status_block=status,
        meta_lines=meta,
        nudge=nudge_line,
        footer=footer,
    )
