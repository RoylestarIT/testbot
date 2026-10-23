from app.core.config import Settings
from app.db.models import SubscriptionPlan


def qr_instructions(settings: Settings, plan: SubscriptionPlan) -> str:
    price = (
        settings.subscription_pro_usd_label
        if plan == SubscriptionPlan.PRO
        else settings.subscription_lite_usd_label
    )
    plan_name = "PRO" if plan == SubscriptionPlan.PRO else "Lite"
    return (
        f"<b>Перевод (РФ / РБ) — {plan_name}</b>\n\n"
        f"Сумма: <b>${price}/мес</b> (эквивалент в ₽ / BYN по курсу банка).\n\n"
        f"{settings.qr_payment_instructions.strip()}\n\n"
        "После оплаты нажмите «Я оплатил». Администратор проверит перевод и активирует подписку."
    )
