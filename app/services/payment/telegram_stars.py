from aiogram.types import LabeledPrice

from app.core.config import Settings
from app.db.models import SubscriptionPlan

STARS_CURRENCY = "XTR"


def invoice_payload(plan: SubscriptionPlan, user_id: int) -> str:
    return f"stars:{plan.value}:{user_id}"


def parse_invoice_payload(payload: str) -> tuple[SubscriptionPlan, int] | None:
    parts = payload.split(":")
    if len(parts) != 3 or parts[0] != "stars":
        return None
    try:
        plan = SubscriptionPlan(parts[1])
        user_id = int(parts[2])
    except (ValueError, KeyError):
        return None
    return plan, user_id


def stars_amount(settings: Settings, plan: SubscriptionPlan) -> int:
    if plan == SubscriptionPlan.PRO:
        return settings.subscription_pro_stars
    return settings.subscription_lite_stars


def invoice_prices(settings: Settings, plan: SubscriptionPlan) -> list[LabeledPrice]:
    amount = stars_amount(settings, plan)
    label = "PRO 1 месяц" if plan == SubscriptionPlan.PRO else "Lite 1 месяц"
    return [LabeledPrice(label=label, amount=amount)]


def invoice_title(plan: SubscriptionPlan) -> str:
    if plan == SubscriptionPlan.PRO:
        return "ReviewPilot PRO"
    return "ReviewPilot Lite"


def invoice_description(plan: SubscriptionPlan, settings: Settings) -> str:
    if plan == SubscriptionPlan.PRO:
        return (
            f"Подписка PRO на 1 месяц (~${settings.subscription_pro_usd_label}/мес). "
            "Без лимита генераций и PRO-функции (авто-публикация — по мере запуска)."
        )
    return (
        f"Подписка Lite на 1 месяц (~${settings.subscription_lite_usd_label}/мес). "
        "Поддержка проекта и доступ к Lite-режиму ответов на отзывы."
    )
