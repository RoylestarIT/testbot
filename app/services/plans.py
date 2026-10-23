from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Subscription, SubscriptionPlan, SubscriptionStatus, User
from app.services.pro_access import has_pro_access, is_trial_pro_active
from app.services.subscription import get_effective_subscription, plan_label

PLANS_COMPARISON_TEXT = (
    "📊 <b>Сравнение тарифов</b>\n\n"
    "<b>Бесплатно</b> — попробовать без оплаты\n"
    "• до <b>5</b> генераций ответов в день\n"
    "• синхронизация WB/Ozon, tone of voice\n"
    "• ответ: <b>скопировать</b> в кабинет вручную\n"
    "• без отправки в API маркетплейса\n\n"
    "✨ <b>Lite</b> (~$10/мес)\n"
    "• <b>без лимита</b> генераций\n"
    "• всё из бесплатного режима\n"
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
    "Lite = генерации без лимита + копирование · "
    "PRO = publish в маркетплейс + авто-ответы"
)


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
