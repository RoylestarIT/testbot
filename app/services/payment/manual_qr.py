from app.core.config import Settings
from app.db.models import SubscriptionPlan
from app.services.payment.fx_rates import SubscriptionPricing


def qr_instructions(
    settings: Settings,
    plan: SubscriptionPlan,
    *,
    pricing: SubscriptionPricing | None = None,
) -> str:
    plan_name = "PRO" if plan == SubscriptionPlan.PRO else "Lite"
    if pricing is not None:
        usd = pricing.pro_usd if plan == SubscriptionPlan.PRO else pricing.lite_usd
        sum_line = f"Сумма: <b>{pricing.format_usd_line(usd)}</b> / мес"
        rate_note = f"\n<i>Курс: {pricing.source}.</i>\n"
    else:
        price = (
            settings.subscription_pro_usd_label
            if plan == SubscriptionPlan.PRO
            else settings.subscription_lite_usd_label
        )
        sum_line = f"Сумма: <b>${price}/мес</b> (эквивалент в ₽ / BYN по курсу банка)."
        rate_note = "\n"
    return (
        f"<b>Перевод (РФ / РБ) — {plan_name}</b>\n\n"
        f"{sum_line}{rate_note}\n"
        f"{settings.qr_payment_instructions.strip()}\n\n"
        "После оплаты нажмите «Я оплатил». Администратор проверит перевод и активирует подписку."
    )
