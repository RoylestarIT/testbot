from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.core.config import get_settings
from app.services.payment.crypto_pay import crypto_pay_enabled, crypto_price_label
from app.services.payment.fx_rates import SubscriptionPricing
from app.services.payment.payment_options import card_payments_enabled, stars_payments_enabled
from app.services.payment.telegram_stars import effective_stars_amount
from app.db.models import SubscriptionPlan


def _truncate_btn(text: str, limit: int = 64) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "…"


def subscription_hub_keyboard(_pricing: SubscriptionPricing | None = None) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="💳 Оплатить", callback_data="sub:pay:menu"),
                InlineKeyboardButton(text="👤 Мой доступ", callback_data="sub:status"),
            ],
            [
                InlineKeyboardButton(text="📊 Тарифы", callback_data="sub:compare"),
                InlineKeyboardButton(text="🧮 Калькулятор", callback_data="sub:calc"),
            ],
            [InlineKeyboardButton(text="🎟 Промокод", callback_data="sub:promo")],
            [InlineKeyboardButton(text="🏠 Сводка", callback_data="menu:dashboard")],
        ]
    )


def subscription_menu_keyboard(pricing: SubscriptionPricing) -> InlineKeyboardMarkup:
    """Алиас для совместимости."""
    return subscription_hub_keyboard(pricing)


def subscription_subscreen_keyboard(*, back: str = "menu:subscription") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="💳 Оплатить", callback_data="sub:pay:menu"),
                InlineKeyboardButton(text="◀️ Подписка", callback_data=back),
            ],
        ]
    )


def payment_methods_keyboard() -> InlineKeyboardMarkup:
    settings = get_settings()
    rows: list[list[InlineKeyboardButton]] = []
    if crypto_pay_enabled(settings):
        rows.append([InlineKeyboardButton(text="🪙 Crypto Bot", callback_data="sub:pay:crypto")])
    if stars_payments_enabled(settings):
        rows.append([InlineKeyboardButton(text="⭐ Telegram Stars", callback_data="sub:pay:stars")])
    rows.append([InlineKeyboardButton(text="💳 Карта РФ / РБ", callback_data="sub:pay:card")])
    rows.append([InlineKeyboardButton(text="◀️ Подписка", callback_data="menu:subscription")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def stars_plan_keyboard(settings=None) -> InlineKeyboardMarkup:
    settings = settings or get_settings()
    lite = effective_stars_amount(settings, SubscriptionPlan.LITE)
    pro = effective_stars_amount(settings, SubscriptionPlan.PRO)
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"✨ Lite · {lite} ⭐",
                    callback_data="sub:stars:lite",
                ),
                InlineKeyboardButton(
                    text=f"🚀 PRO · {pro} ⭐",
                    callback_data="sub:stars:pro",
                ),
            ],
            [InlineKeyboardButton(text="◀️ Способы оплаты", callback_data="sub:pay:menu")],
        ]
    )


def card_payment_keyboard(pricing: SubscriptionPricing) -> InlineKeyboardMarkup:
    settings = get_settings()
    rows: list[list[InlineKeyboardButton]] = []
    if card_payments_enabled(settings):
        cur = settings.payment_currency.upper()
        rows.extend(
            [
                [
                    InlineKeyboardButton(text=f"✨ Lite · {cur}", callback_data="sub:card:lite"),
                    InlineKeyboardButton(text=f"🚀 PRO · {cur}", callback_data="sub:card:pro"),
                ],
            ]
        )
    rows.append(
        [InlineKeyboardButton(text="📋 СБП / перевод", callback_data="sub:pay:transfer")]
    )
    rows.append([InlineKeyboardButton(text="◀️ Способы оплаты", callback_data="sub:pay:menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def crypto_plan_keyboard(settings=None) -> InlineKeyboardMarkup:
    settings = settings or get_settings()
    lite = crypto_price_label(settings, SubscriptionPlan.LITE)
    pro = crypto_price_label(settings, SubscriptionPlan.PRO)
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=_truncate_btn(f"✨ Lite · {lite}"),
                    callback_data="sub:crypto:lite",
                ),
            ],
            [
                InlineKeyboardButton(
                    text=_truncate_btn(f"🚀 PRO · {pro}"),
                    callback_data="sub:crypto:pro",
                ),
            ],
            [InlineKeyboardButton(text="◀️ Способы оплаты", callback_data="sub:pay:menu")],
        ]
    )


def qr_plan_keyboard(pricing: SubscriptionPricing) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=_truncate_btn(f"✨ {pricing.lite_price_label()}"),
                    callback_data="sub:qr:lite",
                ),
                InlineKeyboardButton(
                    text=_truncate_btn(f"🚀 {pricing.pro_price_label()}"),
                    callback_data="sub:qr:pro",
                ),
            ],
            [InlineKeyboardButton(text="◀️ Карта РФ / РБ", callback_data="sub:pay:card")],
        ]
    )


def legal_plan_keyboard(pricing: SubscriptionPricing) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=_truncate_btn(f"✨ {pricing.lite_price_label()}"),
                    callback_data="sub:legal:lite",
                ),
                InlineKeyboardButton(
                    text=_truncate_btn(f"🚀 {pricing.pro_price_label()}"),
                    callback_data="sub:legal:pro",
                ),
            ],
            [InlineKeyboardButton(text="◀️ Способы оплаты", callback_data="sub:pay:menu")],
        ]
    )


def qr_paid_keyboard(plan: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Я оплатил", callback_data=f"sub:qr:paid:{plan}")],
            [InlineKeyboardButton(text="◀️ Назад", callback_data="sub:pay:transfer")],
        ]
    )


def legal_paid_keyboard(plan: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Оплата по счёту", callback_data=f"sub:legal:paid:{plan}")],
            [InlineKeyboardButton(text="◀️ Назад", callback_data="sub:pay:legal")],
        ]
    )


def crypto_pay_keyboard(pay_url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🪙 Оплатить в Crypto Bot", url=pay_url)],
            [InlineKeyboardButton(text="🔄 Проверить оплату", callback_data="sub:crypto:check")],
            [InlineKeyboardButton(text="◀️ Способы оплаты", callback_data="sub:pay:menu")],
        ]
    )
