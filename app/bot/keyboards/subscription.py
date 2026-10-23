from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.core.config import get_settings
from app.services.payment.crypto_pay import crypto_pay_enabled
from app.services.payment.payment_options import card_payments_enabled, stars_payments_enabled
from app.services.payment.telegram_stars import uses_telegram_stars


def _pay_label() -> str:
    settings = get_settings()
    if uses_telegram_stars(settings):
        return "Stars"
    return settings.payment_currency.upper()


def subscription_menu_keyboard() -> InlineKeyboardMarkup:
    settings = get_settings()
    rows: list[list[InlineKeyboardButton]] = []

    if stars_payments_enabled(settings):
        pay = _pay_label()
        rows.extend(
            [
                [
                    InlineKeyboardButton(
                        text=f"✨ Lite · безлимит · {pay}",
                        callback_data="sub:stars:lite",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text=f"💎 PRO · publish + авто · {pay}",
                        callback_data="sub:stars:pro",
                    ),
                ],
            ]
        )
    elif card_payments_enabled(settings):
        pay = _pay_label()
        rows.extend(
            [
                [InlineKeyboardButton(text=f"✨ Lite · {pay}", callback_data="sub:stars:lite")],
                [InlineKeyboardButton(text=f"💎 PRO · {pay}", callback_data="sub:stars:pro")],
            ]
        )

    if crypto_pay_enabled(settings):
        rows.extend(
            [
                [
                    InlineKeyboardButton(
                        text=f"🪙 Lite · ${settings.crypto_lite_amount_usd} USDT/TON…",
                        callback_data="sub:crypto:lite",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text=f"🪙 PRO · ${settings.crypto_pro_amount_usd} USDT/TON…",
                        callback_data="sub:crypto:pro",
                    ),
                ],
            ]
        )

    rows.extend(
        [
            [InlineKeyboardButton(text="📊  Сравнение тарифов", callback_data="sub:compare")],
            [
                InlineKeyboardButton(text="💳  Перевод (РФ / РБ)", callback_data="sub:qr:menu"),
            ],
            [InlineKeyboardButton(text="👤  Мой доступ", callback_data="sub:status")],
            [InlineKeyboardButton(text="🏠  Сводка", callback_data="menu:dashboard")],
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def qr_plan_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✨ Lite $10", callback_data="sub:qr:lite"),
                InlineKeyboardButton(text="💎 PRO $30", callback_data="sub:qr:pro"),
            ],
            [InlineKeyboardButton(text="◀️  Назад", callback_data="menu:subscription")],
        ]
    )


def qr_paid_keyboard(plan: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅  Я оплатил", callback_data=f"sub:qr:paid:{plan}"),
            ],
            [InlineKeyboardButton(text="◀️  Назад", callback_data="menu:subscription")],
        ]
    )


def crypto_pay_keyboard(pay_url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🪙 Оплатить в Crypto Bot", url=pay_url)],
            [InlineKeyboardButton(text="🔄 Проверить оплату", callback_data="sub:crypto:check")],
            [InlineKeyboardButton(text="◀️ Назад", callback_data="menu:subscription")],
        ]
    )
