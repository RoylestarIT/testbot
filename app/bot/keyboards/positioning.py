from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def positioning_keyboard(*, back: str = "menu:dashboard") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📊 Сравнение с рынком", callback_data="menu:market_compare"),
                InlineKeyboardButton(text="🗺 Функции", callback_data="menu:roadmap"),
            ],
            [InlineKeyboardButton(text="◀️ Назад", callback_data=back)],
        ]
    )
