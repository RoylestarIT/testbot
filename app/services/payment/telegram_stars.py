from aiogram.types import LabeledPrice

from app.core.config import Settings
from app.db.models import PaymentMethod, SubscriptionPlan

STARS_CURRENCY = "XTR"
PAYLOAD_PREFIX = "sub"


def fiat_invoices_configured(settings: Settings) -> bool:
    return bool(settings.payment_provider_token.strip())


def stars_invoices_configured(settings: Settings) -> bool:
    return settings.payment_enable_stars


def uses_telegram_stars(settings: Settings) -> bool:
    """Legacy: только Stars, без провайдера карт (нет PAYMENT_PROVIDER_TOKEN)."""
    return not fiat_invoices_configured(settings) and stars_invoices_configured(settings)


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


def effective_stars_amount(settings: Settings, plan: SubscriptionPlan) -> int:
    """Stars: явный SUBSCRIPTION_*_STARS или ₽ × (1 + markup%), округление."""
    manual = (
        settings.subscription_pro_stars
        if plan == SubscriptionPlan.PRO
        else settings.subscription_lite_stars
    )
    if manual is not None:
        return manual
    rub = (
        settings.subscription_pro_price_rub
        if plan == SubscriptionPlan.PRO
        else settings.subscription_lite_price_rub
    )
    factor = 1.0 + settings.subscription_stars_markup_percent / 100.0
    return max(1, round(rub * factor))


def stars_invoice_amount(settings: Settings, plan: SubscriptionPlan) -> int:
    return effective_stars_amount(settings, plan)


def fiat_invoice_amount(settings: Settings, plan: SubscriptionPlan) -> int:
    if plan == SubscriptionPlan.PRO:
        return settings.subscription_pro_price_minor
    return settings.subscription_lite_price_minor


def invoice_amount(settings: Settings, plan: SubscriptionPlan, *, for_stars: bool) -> int:
    if for_stars:
        return stars_invoice_amount(settings, plan)
    return fiat_invoice_amount(settings, plan)


def invoice_prices(settings: Settings, plan: SubscriptionPlan, *, for_stars: bool) -> list[LabeledPrice]:
    amount = invoice_amount(settings, plan, for_stars=for_stars)
    label = "PRO 1 месяц" if plan == SubscriptionPlan.PRO else "Lite 1 месяц"
    return [LabeledPrice(label=label, amount=amount)]


def invoice_currency(*, for_stars: bool, settings: Settings | None = None) -> str:
    if for_stars:
        return STARS_CURRENCY
    assert settings is not None
    return settings.payment_currency.upper()


def invoice_provider_token(*, for_stars: bool, settings: Settings | None = None) -> str:
    if for_stars:
        return ""
    assert settings is not None
    return settings.payment_provider_token.strip()


def payment_method_for_currency(currency: str) -> PaymentMethod:
    if currency.upper() == STARS_CURRENCY:
        return PaymentMethod.STARS
    return PaymentMethod.TELEGRAM


def payment_method_for_invoice(settings: Settings, *, for_stars: bool) -> PaymentMethod:
    if for_stars:
        return PaymentMethod.STARS
    return PaymentMethod.TELEGRAM


def invoice_title(plan: SubscriptionPlan) -> str:
    if plan == SubscriptionPlan.PRO:
        return "ReviewPilot PRO"
    return "ReviewPilot Lite"


def invoice_description(plan: SubscriptionPlan, settings: Settings, *, for_stars: bool) -> str:
    if for_stars:
        stars = stars_invoice_amount(settings, plan)
        if plan == SubscriptionPlan.PRO:
            return (
                f"PRO на 1 месяц — {stars} Telegram Stars. "
                "Без дневного лимита, отправка в WB/Ozon из бота, авто-ответы 4–5★."
            )
        return (
            f"Lite на 1 месяц — {stars} Telegram Stars. "
            "Без дневного лимита; ответ в кабинет — копированием."
        )
    if plan == SubscriptionPlan.PRO:
        return (
            f"PRO на 1 месяц — {settings.subscription_pro_price_rub} ₽ / "
            f"{settings.subscription_pro_price_byn:g} BYN. "
            "Без дневного лимита, отправка в WB/Ozon из бота, авто-ответы 4–5★."
        )
    return (
        f"Lite на 1 месяц — {settings.subscription_lite_price_rub} ₽ / "
        f"{settings.subscription_lite_price_byn:g} BYN. "
        "Без дневного лимита; ответ в кабинет — копированием."
    )


def payment_mode_label(settings: Settings, *, for_stars: bool | None = None) -> str:
    if for_stars is True:
        return "Telegram Stars"
    if for_stars is False:
        return f"Telegram Payments ({settings.payment_currency.upper()})"
    if uses_telegram_stars(settings):
        return "Telegram Stars"
    if stars_invoices_configured(settings) and not fiat_invoices_configured(settings):
        return "Telegram Stars"
    return f"Telegram Payments ({settings.payment_currency.upper()})"


def payment_mode_label_for_currency(currency: str, settings: Settings) -> str:
    if currency.upper() == STARS_CURRENCY:
        return "Telegram Stars"
    return f"Telegram Payments ({currency.upper()})"
