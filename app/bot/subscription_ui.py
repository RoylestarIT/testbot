"""Экраны подписки — одна точка входа, без простыней."""

from __future__ import annotations

from app.bot.ui import brand_title, muted, quote
from app.services.payment.fx_rates import SubscriptionPricing, _fmt_rub

SUBSCRIPTION_SEP = "───────────────"


def build_subscription_hub(pricing: SubscriptionPricing, *, access_line: str) -> str:
    lite = pricing.format_usd_line(pricing.lite_usd)
    pro = pricing.format_usd_line(pricing.pro_usd)
    return (
        f"{brand_title('Подписка', tagline='Фикс в месяц · WB/Ozon', icon='💎').strip()}\n"
        f"{SUBSCRIPTION_SEP}\n\n"
        f"{quote(f'👤  {access_line}')}\n\n"
        f"✨  Lite — {lite}\n"
        f"🚀  PRO — {pro}\n\n"
        f"{muted('Оплата: крипта · карта РФ/РБ · безнал для юр. лиц')}"
    )


def build_payment_hub(pricing: SubscriptionPricing) -> str:
    return (
        f"{brand_title('Оплата', tagline='Выберите способ', icon='💳').strip()}\n"
        f"{SUBSCRIPTION_SEP}\n\n"
        f"✨  Lite — {pricing.format_usd_line(pricing.lite_usd)}\n"
        f"🚀  PRO — {pricing.format_usd_line(pricing.pro_usd)}\n\n"
        f"{muted('После оплаты проверьте «Мой доступ».')}"
    )
