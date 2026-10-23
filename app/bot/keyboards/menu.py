from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Отзывы", callback_data="menu:reviews"),
            ],
            [
                InlineKeyboardButton(text="Настройки", callback_data="menu:settings"),
                InlineKeyboardButton(text="Подписка", callback_data="menu:subscription"),
            ],
            [
                InlineKeyboardButton(text="Помощь", callback_data="menu:help"),
            ],
        ]
    )
