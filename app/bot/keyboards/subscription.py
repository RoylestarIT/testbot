from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.core.config import get_settings
from app.services.payment.crypto_pay import crypto_pay_enabled
from app.services.payment.fx_rates import SubscriptionPricing
from app.services.payment.payment_options import card_payments_enabled, stars_payments_enabled
from app.services.payment.telegram_stars import uses_telegram_stars


def _pay_label() -> str:
    settings = get_settings()
    if uses_telegram_stars(settings):
        return "Stars"
    return settings.payment_currency.upper()


def _truncate_btn(text: str, limit: int = 64) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "…"


def subscription_menu_keyboard(pricing: SubscriptionPricing) -> InlineKeyboardMarkup:
    """Главное меню подписки — без кнопок оплаты тарифов."""
    _ = pricing
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📊  Сравнение тарифов", callback_data="sub:compare")],
            [InlineKeyboardButton(text="💳  Способ оплаты", callback_data="sub:pay:menu")],
            [InlineKeyboardButton(text="👤  Мой доступ", callback_data="sub:status")],
            [InlineKeyboardButton(text="🏠  Сводка", callback_data="menu:dashboard")],
        ]
    )


def payment_methods_keyboard() -> InlineKeyboardMarkup:
    settings = get_settings()
    rows: list[list[InlineKeyboardButton]] = []
    if crypto_pay_enabled(settings):
        rows.append(
            [InlineKeyboardButton(text="🪙  Криптовалюта (Crypto Bot)", callback_data="sub:pay:crypto")]
        )
    rows.append(
        [InlineKeyboardButton(text="💳  Карта · РФ / РБ", callback_data="sub:pay:card")]
    )
    rows.append(
        [InlineKeyboardButton(text="🏦  Безнал · юр. лицо", callback_data="sub:pay:legal")]
    )
    rows.append([InlineKeyboardButton(text="◀️  Подписка", callback_data="menu:subscription")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def card_payment_keyboard(pricing: SubscriptionPricing) -> InlineKeyboardMarkup:
    settings = get_settings()
    rows: list[list[InlineKeyboardButton]] = []
    if stars_payments_enabled(settings) or card_payments_enabled(settings):
        pay = _pay_label()
        rows.extend(
            [
                [InlineKeyboardButton(text=f"✨ Lite · {pay}", callback_data="sub:stars:lite")],
                [InlineKeyboardButton(text=f"💎 PRO · {pay}", callback_data="sub:stars:pro")],
            ]
        )
    rows.append(
        [
            InlineKeyboardButton(
                text="📋  СБП / перевод на реквизиты",
                callback_data="sub:pay:transfer",
            )
        ]
    )
    rows.append([InlineKeyboardButton(text="◀️  Способы оплаты", callback_data="sub:pay:menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def crypto_plan_keyboard(pricing: SubscriptionPricing) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=_truncate_btn(pricing.crypto_lite_button()),
                    callback_data="sub:crypto:lite",
                ),
            ],
            [
                InlineKeyboardButton(
                    text=_truncate_btn(pricing.crypto_pro_button()),
                    callback_data="sub:crypto:pro",
                ),
            ],
            [InlineKeyboardButton(text="◀️  Способы оплаты", callback_data="sub:pay:menu")],
        ]
    )


def qr_plan_keyboard(pricing: SubscriptionPricing) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=_truncate_btn(pricing.lite_line()),
                    callback_data="sub:qr:lite",
                ),
            ],
            [
                InlineKeyboardButton(
                    text=_truncate_btn(pricing.pro_line()),
                    callback_data="sub:qr:pro",
                ),
            ],
            [InlineKeyboardButton(text="◀️  Карта · РФ / РБ", callback_data="sub:pay:card")],
        ]
    )


def legal_plan_keyboard(pricing: SubscriptionPricing) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=_truncate_btn(pricing.lite_line()),
                    callback_data="sub:legal:lite",
                ),
            ],
            [
                InlineKeyboardButton(
                    text=_truncate_btn(pricing.pro_line()),
                    callback_data="sub:legal:pro",
                ),
            ],
            [InlineKeyboardButton(text="◀️  Способы оплаты", callback_data="sub:pay:menu")],
        ]
    )


def qr_paid_keyboard(plan: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅  Я оплатил", callback_data=f"sub:qr:paid:{plan}")],
            [InlineKeyboardButton(text="◀️  Назад", callback_data="sub:pay:transfer")],
        ]
    )


def legal_paid_keyboard(plan: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅  Я оплатил по счёту", callback_data=f"sub:legal:paid:{plan}")],
            [InlineKeyboardButton(text="◀️  Назад", callback_data="sub:pay:legal")],
        ]
    )


def crypto_pay_keyboard(pay_url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🪙 Оплатить в Crypto Bot", url=pay_url)],
            [InlineKeyboardButton(text="🔄 Проверить оплату", callback_data="sub:crypto:check")],
            [InlineKeyboardButton(text="◀️  Способы оплаты", callback_data="sub:pay:menu")],
        ]
    )
