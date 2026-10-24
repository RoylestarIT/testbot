from app.core.config import Settings
from app.db.models import SubscriptionPlan
from app.services.payment.fx_rates import SubscriptionPricing


def _sum_line(pricing: SubscriptionPricing, plan: SubscriptionPlan, *, legal: bool) -> str:
    label = pricing.pro_price_label() if plan == SubscriptionPlan.PRO else pricing.lite_price_label()
    suffix = " / мес (безнал)" if legal else " / мес"
    return f"Сумма: <b>{label}</b>{suffix}"


def _sum_line_from_settings(settings: Settings, plan: SubscriptionPlan) -> str:
    if plan == SubscriptionPlan.PRO:
        return f"Сумма: <b>{settings.subscription_pro_price_rub} ₽ / {settings.subscription_pro_price_byn:g} BYN</b> / мес"
    return f"Сумма: <b>{settings.subscription_lite_price_rub} ₽ / {settings.subscription_lite_price_byn:g} BYN</b> / мес"


def qr_instructions(
    settings: Settings,
    plan: SubscriptionPlan,
    *,
    pricing: SubscriptionPricing | None = None,
) -> str:
    plan_name = "PRO" if plan == SubscriptionPlan.PRO else "Lite"
    sum_line = _sum_line(pricing, plan, legal=False) if pricing else _sum_line_from_settings(settings, plan)
    return (
        f"<b>Перевод (РФ / РБ) — {plan_name}</b>\n\n"
        f"{sum_line}\n\n"
        f"{settings.qr_payment_instructions.strip()}\n\n"
        f"После оплаты нажмите «Я оплатил». Активация — обычно до "
        f"<b>{settings.payment_activation_sla_hours}</b> ч (рабочее время).\n"
        "Администратор сверит перевод и включит тариф."
    )


def legal_payment_instructions(
    settings: Settings,
    plan: SubscriptionPlan,
    *,
    pricing: SubscriptionPricing | None = None,
) -> str:
    plan_name = "PRO" if plan == SubscriptionPlan.PRO else "Lite"
    sum_line = _sum_line(pricing, plan, legal=True) if pricing else _sum_line_from_settings(settings, plan)
    return (
        f"<b>Безнал · юр. лицо — {plan_name}</b>\n\n"
        f"{sum_line}\n\n"
        f"{settings.legal_payment_instructions.strip()}\n\n"
        f"После оплаты по счёту нажмите «Я оплатил». Активация — до "
        f"<b>{settings.payment_activation_sla_hours}</b> ч после поступления средств."
    )
