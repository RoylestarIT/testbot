from aiogram.types import LabeledPrice

from app.core.config import Settings
from app.db.models import PaymentMethod, SubscriptionPlan

STARS_CURRENCY = "XTR"
PAYLOAD_PREFIX = "sub"


def uses_telegram_stars(settings: Settings) -> bool:
    return not settings.payment_provider_token.strip()


def invoice_provider_token(settings: Settings) -> str:
    if uses_telegram_stars(settings):
        return ""
    return settings.payment_provider_token.strip()


def invoice_currency(settings: Settings) -> str:
    if uses_telegram_stars(settings):
        return STARS_CURRENCY
    return settings.payment_currency.upper()


def payment_method_for_invoice(settings: Settings) -> PaymentMethod:
    if uses_telegram_stars(settings):
        return PaymentMethod.STARS
    return PaymentMethod.TELEGRAM


def invoice_payload(plan: SubscriptionPlan, user_id: int) -> str:
    return f"{PAYLOAD_PREFIX}:{plan.value}:{user_id}"


def parse_invoice_payload(payload: str) -> tuple[SubscriptionPlan, int] | None:
    parts = payload.split(":")
    if len(parts) != 3:
        return None
    if parts[0] not in (PAYLOAD_PREFIX, "stars"):
        return None
    try:
        plan = SubscriptionPlan(parts[1])
        user_id = int(parts[2])
    except (ValueError, KeyError):
        return None
    return plan, user_id


def invoice_amount(settings: Settings, plan: SubscriptionPlan) -> int:
    if uses_telegram_stars(settings):
        if plan == SubscriptionPlan.PRO:
            return settings.subscription_pro_stars
        return settings.subscription_lite_stars
    if plan == SubscriptionPlan.PRO:
        return settings.subscription_pro_price_minor
    return settings.subscription_lite_price_minor


def invoice_prices(settings: Settings, plan: SubscriptionPlan) -> list[LabeledPrice]:
    amount = invoice_amount(settings, plan)
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


def payment_mode_label(settings: Settings) -> str:
    if uses_telegram_stars(settings):
        return "Telegram Stars"
    return f"Telegram Payments ({invoice_currency(settings)})"
