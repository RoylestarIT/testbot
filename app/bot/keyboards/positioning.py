from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def positioning_keyboard(*, back: str = "menu:dashboard") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📊 Сравнение", callback_data="menu:market_compare"),
            ],
            [
                InlineKeyboardButton(text="🎯 Для кого", callback_data="menu:for_whom"),
            ],
            [
                InlineKeyboardButton(text="🗺 Функции", callback_data="menu:roadmap"),
            ],
            [
                InlineKeyboardButton(text="💎 Подписка", callback_data="menu:subscription"),
                InlineKeyboardButton(text="◀️ Сводка", callback_data=back),
            ],
        ]
    )
