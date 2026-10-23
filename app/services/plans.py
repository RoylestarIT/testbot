from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.constants import MANUAL_SHOP_NAME
from app.db.models import Marketplace, Subscription, SubscriptionPlan, SubscriptionStatus, User
from app.db.repositories.account import AccountRepository
from app.db.repositories.tone_profile import ToneProfileRepository
from app.services.pro_access import has_pro_access, is_trial_pro_active
from app.services.subscription import get_effective_subscription, plan_label

FREE_MAX_MARKETPLACE_ACCOUNTS = 1
FREE_MAX_TONE_PROFILES = 1

PLANS_COMPARISON_TEXT = (
    "📊 <b>Сравнение тарифов</b>\n\n"
    "<b>Бесплатно</b> — попробовать без оплаты\n"
    "• до <b>5</b> генераций ответов в день\n"
    f"• <b>{FREE_MAX_MARKETPLACE_ACCOUNTS}</b> кабинет WB/Ozon\n"
    f"• <b>{FREE_MAX_TONE_PROFILES}</b> профиль tone of voice\n"
    "• синхронизация отзывов\n"
    "• ответ: <b>скопировать</b> в кабинет вручную\n"
    "• без отправки в API маркетплейса\n\n"
    "✨ <b>Lite</b> (~$10/мес)\n"
    "• <b>без лимита</b> генераций\n"
    "• <b>несколько</b> кабинетов и tone-профилей\n"
    "• публикация только <b>копированием</b> (не из бота)\n\n"
    "🚀 <b>PRO</b> (~$30/мес)\n"
    "• без лимита генераций\n"
    "• <b>отправка ответа</b> в WB/Ozon из бота\n"
    "• <b>авто-ответы</b> на отзывы 4–5★ (в настройках)\n"
    "• приоритет для новых PRO-функций\n\n"
    "🎁 <b>Trial PRO</b> — один раз на аккаунт, как PRO на срок trial "
    "(кнопка в «Сводке», если доступна).\n\n"
    "<i>Без PRO: иногда доступны несколько бесплатных publish в API — "
    "смотрите «Сводку».</i>"
)

LITE_VS_PRO_SHORT = (
    "Lite = ∞ генераций, несколько кабинетов/tone · "
    "PRO = publish в маркетплейс + авто-ответы"
)

UPSELL_LITE_OR_PRO = "Оформите Lite или PRO: «Подписка» → Сравнение тарифов."


async def has_lite_or_higher(session: AsyncSession, user_id: int) -> bool:
    """Платный Lite, PRO или активный trial — без лимитов кабинетов и tone."""
    return await has_unlimited_generations(session, user_id)


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
    if await has_lite_or_higher(session, user_id):
        return True, None
    count = await count_user_api_accounts(session, user_id)
    if count >= FREE_MAX_MARKETPLACE_ACCOUNTS:
        return (
            False,
            f"На бесплатном тарифе — только {FREE_MAX_MARKETPLACE_ACCOUNTS} кабинет WB/Ozon. "
            + UPSELL_LITE_OR_PRO,
        )
    return True, None


async def can_add_tone_profile(session: AsyncSession, user_id: int) -> tuple[bool, str | None]:
    if await has_lite_or_higher(session, user_id):
        return True, None
    count = await count_user_tone_profiles(session, user_id)
    if count >= FREE_MAX_TONE_PROFILES:
        return (
            False,
            f"На бесплатном тарифе — только {FREE_MAX_TONE_PROFILES} профиль tone. "
            + UPSELL_LITE_OR_PRO,
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


async def describe_access_tier(
    session: AsyncSession,
    user: User,
    subscription: Subscription | None,
) -> str:
    if subscription and subscription.status == SubscriptionStatus.ACTIVE:
        if subscription.plan == SubscriptionPlan.PRO:
            return f"💎 Тариф: <b>{plan_label(subscription.plan)}</b> (оплачен)"
        return f"✨ Тариф: <b>{plan_label(subscription.plan)}</b> (оплачен)"
    if await is_trial_pro_active(user):
        until = user.trial_pro_until.strftime("%d.%m.%Y") if user.trial_pro_until else "—"
        return f"🎁 Trial PRO до <b>{until}</b>"
    return "🆓 Режим: <b>бесплатный</b> (Lite без оплаты)"
