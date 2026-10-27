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
from app.services.pro_access import is_trial_pro_active
from app.services.subscription import get_effective_subscription


def _sync_line(account) -> str:
    mp = "🟣 WB" if account.marketplace == Marketplace.WB else "🔵 Ozon"
    name = account.shop_name or f"#{account.id}"
    if not account.is_active:
        status = "нужен новый ключ"
    elif account.last_sync_error:
        status = account.last_sync_error[:60]
    else:
        status = "всё ок"
    sync_at = (
        f"обновлено {format_ui_time(account.last_sync_at)} (Минск)"
        if account.last_sync_at
        else "ещё не обновляли"
    )
    return f"{mp} <b>{name}</b> — {sync_at} · {status}"


def _plan_extra_line(user: User, subscription) -> str | None:
    if is_trial_pro_active(user):
        until = user.trial_pro_until.strftime("%d.%m.%Y") if user.trial_pro_until else "—"
        return f"🎁 Пробный PRO до {until} — ответы можно отправлять в маркетплейс из бота."
    if subscription and subscription.status.value == "active":
        if subscription.plan == SubscriptionPlan.PRO:
            return "💎 PRO — отправка в WB/Ozon и авто-ответы на 4–5★."
        if subscription.plan == SubscriptionPlan.LITE:
            return "✨ Lite — без дневного лимита; в маркетплейс — копированием."
    if user.free_api_publishes_remaining > 0:
        return (
            f"🚀 На бесплатном тарифе осталось <b>{user.free_api_publishes_remaining}</b> пробных отправок "
            "в маркетплейс из бота."
        )
    return "На бесплатном тарифе ответы копируете в кабинет WB/Ozon; PRO — отправка из бота."


async def build_dashboard_details(session: AsyncSession, user: User) -> str:
    subscription = await get_effective_subscription(session, user.id)
    tier = await describe_access_tier(session, user, subscription)
    analytics = await build_period_analytics_block(session, user.id)
    accounts_all = await AccountRepository(session).list_by_user_id(user.id, active_only=True)
    q_sum = sum(a.cached_unanswered_questions for a in accounts_all if a.marketplace.value == "wb")
    questions_line = (
        f"❓  Без ответа в WB: <b>{q_sum}</b> вопрос(ов) покупателей"
        if q_sum
        else "❓  Новых вопросов покупателей на WB нет"
    )
    lines = [
        brand_title("Подробнее", tagline="Тариф, очередь и кабинеты", icon="📊"),
        "",
        f"💎  Тариф: <b>{tier}</b>",
    ]
    extra = _plan_extra_line(user, subscription)
    if extra:
        lines.append(muted(extra))
    lines.extend(
        [
            "",
            analytics,
            "",
            questions_line,
            "",
            "<b>🏪 Кабинеты</b>",
        ]
    )

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
        lines.append(muted("Подключите WB или Ozon в ⚙️ Настройки."))

    if not await has_lite_or_higher(session, user.id):
        acc_n = await count_user_api_accounts(session, user.id)
        tone_n = await count_user_tone_profiles(session, user.id)
        lines.extend(
            [
                "",
                "<b>🔒 Лимиты бесплатного тарифа</b>",
                bullet(f"Кабинеты: {acc_n} из {FREE_MAX_MARKETPLACE_ACCOUNTS}"),
                bullet(f"Профили тона: {tone_n} из {FREE_MAX_TONE_PROFILES}"),
            ]
        )
    return "\n".join(lines)
