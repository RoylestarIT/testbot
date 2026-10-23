from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def subscription_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⭐ Lite — Stars ($10/мес)", callback_data="sub:stars:lite"),
            ],
            [
                InlineKeyboardButton(text="⭐ PRO — Stars ($30/мес)", callback_data="sub:stars:pro"),
            ],
            [
                InlineKeyboardButton(text="Оплатить по QR (РБ)", callback_data="sub:qr:menu"),
            ],
            [
                InlineKeyboardButton(text="Моя подписка", callback_data="sub:status"),
            ],
            [
                InlineKeyboardButton(text="← Главное меню", callback_data="menu:main"),
            ],
        ]
    )


def qr_plan_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Lite ($10/мес)", callback_data="sub:qr:lite"),
                InlineKeyboardButton(text="PRO ($30/мес)", callback_data="sub:qr:pro"),
            ],
            [InlineKeyboardButton(text="← Назад", callback_data="menu:subscription")],
        ]
    )


def qr_paid_keyboard(plan: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Я оплатил", callback_data=f"sub:qr:paid:{plan}"),
            ],
            [InlineKeyboardButton(text="← Назад", callback_data="menu:subscription")],
        ]
    )
