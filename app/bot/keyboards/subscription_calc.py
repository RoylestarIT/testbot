from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.services.payment.subscription_calculator import PRESET_VOLUMES


def calculator_volumes_keyboard() -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    chunk: list[InlineKeyboardButton] = []
    for vol in PRESET_VOLUMES:
        chunk.append(
            InlineKeyboardButton(text=f"{vol} отв.", callback_data=f"sub:calc:{vol}")
        )
        if len(chunk) == 3:
            rows.append(chunk)
            chunk = []
    if chunk:
        rows.append(chunk)
    rows.append([InlineKeyboardButton(text="◀️ Подписка", callback_data="menu:subscription")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def calculator_detail_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="◀️ К таблице", callback_data="sub:calc")],
            [InlineKeyboardButton(text="💳 Способ оплаты", callback_data="sub:pay:menu")],
        ]
    )
