from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.constants import MANUAL_SHOP_NAME
from app.db.models import Marketplace, Subscription, SubscriptionPlan, SubscriptionStatus, User
from app.db.repositories.account import AccountRepository
from app.db.repositories.tone_profile import ToneProfileRepository
from app.services.pro_access import has_pro_access, is_trial_pro_active
from app.bot.ui import brand_title, bullet, muted, section
from app.services.subscription import get_effective_subscription, plan_label

FREE_MAX_MARKETPLACE_ACCOUNTS = 1
LITE_MAX_MARKETPLACE_ACCOUNTS = 2
PRO_MAX_MARKETPLACE_ACCOUNTS = 4
FREE_MAX_TONE_PROFILES = 1

PLANS_COMPARISON_TEXT = (
    brand_title("Тарифы", tagline="Что входит", icon="📊")
    + section("Бесплатный", icon="🆓")
    + "\n"
    + bullet("5 подготовленных ответов в день · 1 кабинет · 1 профиль тона")
    + "\n"
    + bullet("ответ — копирование в кабинет")
    + section("Lite", icon="✨")
    + "\n"
    + bullet(f"без дневного лимита · до {LITE_MAX_MARKETPLACE_ACCOUNTS} кабинетов · профили тона")
    + "\n"
    + bullet("отправка только копированием в кабинет")
    + section("PRO", icon="🚀")
    + "\n"
    + bullet(f"до {PRO_MAX_MARKETPLACE_ACCOUNTS} кабинетов WB/Ozon")
    + "\n"
    + bullet("отправка ответа из бота в WB/Ozon")
    + "\n"
    + bullet("авто-ответы 4–5★ · низкие оценки только вручную")
    + "\n"
    + muted("Lite — 990 ₽ / 35 BYN · PRO — 1 990 ₽ / 70 BYN в месяц.")
    + "\n"
    + muted("Пробный PRO — кнопка на сводке · один раз на аккаунт.")
)

LITE_VS_PRO_SHORT = (
    f"Lite: до {LITE_MAX_MARKETPLACE_ACCOUNTS} кабинетов, копирование · "
    f"PRO: до {PRO_MAX_MARKETPLACE_ACCOUNTS} кабинетов, отправка из бота + авто 4–5★"
)

UPSELL_LITE_OR_PRO = "Оформите Lite или PRO: «Подписка» → сравнение тарифов."


async def has_lite_or_higher(session: AsyncSession, user_id: int) -> bool:
    """Платный Lite, PRO или активный trial — без лимита ответов и профилей тона."""
    return await has_unlimited_generations(session, user_id)


async def max_marketplace_accounts(session: AsyncSession, user_id: int) -> int:
    if await has_pro_access(session, user_id):
        return PRO_MAX_MARKETPLACE_ACCOUNTS
    if await has_active_lite_subscription(session, user_id):
        return LITE_MAX_MARKETPLACE_ACCOUNTS
    return FREE_MAX_MARKETPLACE_ACCOUNTS


async def count_user_api_accounts(session: AsyncSession, user_id: int) -> int:
    accounts = await AccountRepository(session).list_by_user_id(user_id)
    return sum(
        1
        for account in accounts
        if account.marketplace in (Marketplace.WB, Marketplace.OZON)
        and (account.shop_name is None or account.shop_name != MANUAL_SHOP_NAME)
    )


async def count_user_tone_profiles(session: AsyncSession, user_id: int) -> int:
    profiles = await ToneProfileRepository(session).list_by_user_id(user_id)
    return len(profiles)


async def can_add_marketplace_account(session: AsyncSession, user_id: int) -> tuple[bool, str | None]:
    limit = await max_marketplace_accounts(session, user_id)
    count = await count_user_api_accounts(session, user_id)
    if count < limit:
        return True, None
    if limit == FREE_MAX_MARKETPLACE_ACCOUNTS:
        return (
            False,
            f"На бесплатном тарифе — только {limit} кабинет WB/Ozon. " + UPSELL_LITE_OR_PRO,
        )
    if limit == LITE_MAX_MARKETPLACE_ACCOUNTS:
        return (
            False,
            f"На тарифе Lite — до {limit} кабинетов WB/Ozon. "
            "Оформите PRO — до 4 кабинетов: «Подписка» → сравнение тарифов.",
        )
    return (
        False,
        f"На тарифе PRO — до {PRO_MAX_MARKETPLACE_ACCOUNTS} кабинетов WB/Ozon.",
    )


async def can_add_tone_profile(session: AsyncSession, user_id: int) -> tuple[bool, str | None]:
    if await has_lite_or_higher(session, user_id):
        return True, None
    count = await count_user_tone_profiles(session, user_id)
    if count >= FREE_MAX_TONE_PROFILES:
        return (
            False,
            f"На бесплатном тарифе — {FREE_MAX_TONE_PROFILES} профиль тона. " + UPSELL_LITE_OR_PRO,
        )
    return True, None


async def has_active_lite_subscription(session: AsyncSession, user_id: int) -> bool:
    subscription = await get_effective_subscription(session, user_id)
    return (
        subscription is not None
        and subscription.status == SubscriptionStatus.ACTIVE
        and subscription.plan == SubscriptionPlan.LITE
    )


async def has_unlimited_generations(session: AsyncSession, user_id: int) -> bool:
    if await has_pro_access(session, user_id):
        return True
    return await has_active_lite_subscription(session, user_id)


async def describe_access_tier(session: AsyncSession, user: User, subscription: Subscription | None) -> str:
    if subscription and subscription.status == SubscriptionStatus.ACTIVE:
        name = plan_label(subscription.plan)
        until = subscription.expires_at.strftime("%d.%m.%Y") if subscription.expires_at else "—"
        return f"{name} до {until}"
    if await is_trial_pro_active(user):
        until = user.trial_pro_until.strftime("%d.%m.%Y") if user.trial_pro_until else "—"
        return f"Пробный PRO до {until}"
    return "Бесплатный"
