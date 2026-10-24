from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.ui import brand_title, bullet, muted
from app.tasks.poller import format_ui_time
from app.constants import MANUAL_SHOP_NAME
from app.db.models import Marketplace, SubscriptionPlan, User
from app.db.repositories.account import AccountRepository
from app.services.plans import (
    FREE_MAX_MARKETPLACE_ACCOUNTS,
    FREE_MAX_TONE_PROFILES,
    count_user_api_accounts,
    count_user_tone_profiles,
    describe_access_tier,
    has_lite_or_higher,
)
from app.services.period_analytics import build_period_analytics_block
from app.services.subscription import get_effective_subscription


def _sync_line(account) -> str:
    mp = "🟣 WB" if account.marketplace == Marketplace.WB else "🔵 Ozon"
    name = account.shop_name or f"#{account.id}"
    if not account.is_active:
        status = "⚠️ ключ не принят / отключён"
    elif account.last_sync_error:
        status = f"⚠️ {account.last_sync_error[:80]}"
    else:
        status = "✅ OK"
    sync_at = (
        f"{format_ui_time(account.last_sync_at)} (Минск)"
        if account.last_sync_at
        else "ещё не было"
    )
    return f"{mp} <b>{name}</b> — sync {sync_at} · {status}"


async def build_dashboard_details(session: AsyncSession, user: User) -> str:
    subscription = await get_effective_subscription(session, user.id)
    tier = await describe_access_tier(session, user, subscription)
    analytics = await build_period_analytics_block(session, user.id)
    accounts_all = await AccountRepository(session).list_by_user_id(user.id, active_only=True)
    q_sum = sum(a.cached_unanswered_questions for a in accounts_all if a.marketplace.value == "wb")
    questions_line = (
        f"❓  Вопросы WB без ответа: <b>{q_sum}</b>" if q_sum else "❓  Новых вопросов WB нет"
    )
    lines = [
        brand_title("Подробнее", tagline="Тариф, аналитика, кабинеты", icon="📊"),
        bullet(f"💎 Тариф: <b>{tier}</b>"),
        bullet(f"🚀 Publish-квота: <b>{user.free_api_publishes_remaining}</b>"),
        "",
        analytics,
        questions_line,
        "",
        "<b>🏪 Кабинеты</b>",
    ]

    all_accounts = await AccountRepository(session).list_by_user_id(user.id)
    accounts = [
        a
        for a in all_accounts
        if a.marketplace in (Marketplace.WB, Marketplace.OZON)
        and (a.shop_name is None or a.shop_name != MANUAL_SHOP_NAME)
    ]
    if accounts:
        for acc in accounts[:8]:
            lines.append(bullet(_sync_line(acc)))
        if len(accounts) > 8:
            lines.append(muted(f"… и ещё {len(accounts) - 8}"))
    else:
        lines.append(muted("Кабинеты не подключены — ⚙️ Настройки"))

    if not await has_lite_or_higher(session, user.id):
        acc_n = await count_user_api_accounts(session, user.id)
        tone_n = await count_user_tone_profiles(session, user.id)
        lines.extend(
            [
                "",
                "<b>🔒 Лимиты Free</b>",
                bullet(f"Кабинеты: {acc_n}/{FREE_MAX_MARKETPLACE_ACCOUNTS}"),
                bullet(f"Тон ответа: {tone_n}/{FREE_MAX_TONE_PROFILES}"),
            ]
        )
    elif subscription and subscription.status.value == "active":
        if subscription.plan == SubscriptionPlan.LITE:
            lines.append("")
            lines.append(muted("✨ Lite — генерации без лимита, publish только копированием."))
        elif subscription.plan == SubscriptionPlan.PRO:
            lines.append("")
            lines.append(
                muted("💎 PRO — publish в API; авто только 4–5★, негатив — вручную.")
            )

    return "\n".join(lines)
