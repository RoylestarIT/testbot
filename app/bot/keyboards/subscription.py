from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.core.config import get_settings
from app.services.payment.telegram_stars import uses_telegram_stars


def _pay_label() -> str:
    settings = get_settings()
    if uses_telegram_stars(settings):
        return "Stars"
    return settings.payment_currency.upper()


def subscription_menu_keyboard() -> InlineKeyboardMarkup:
    pay = _pay_label()
    return InlineKeyboardMarkup(
        inline_keyboard=[
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
            [
                InlineKeyboardButton(text="📊  Сравнение тарифов", callback_data="sub:compare"),
            ],
            [
                InlineKeyboardButton(text="💳  Оплата QR (РБ)", callback_data="sub:qr:menu"),
            ],
            [
                InlineKeyboardButton(text="👤  Мой доступ", callback_data="sub:status"),
            ],
            [
                InlineKeyboardButton(text="🏠  Сводка", callback_data="menu:main"),
            ],
        ]
    )


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
