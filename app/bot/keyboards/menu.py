from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu_keyboard(*, show_admin: bool = False) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = [
        [InlineKeyboardButton(text="Отзывы", callback_data="menu:reviews")],
        [
            InlineKeyboardButton(text="Настройки", callback_data="menu:settings"),
            InlineKeyboardButton(text="Подписка", callback_data="menu:subscription"),
        ],
    ]
    if show_admin:
        rows.append([InlineKeyboardButton(text="🛠 Админ-панель", callback_data="menu:admin")])
    rows.append([InlineKeyboardButton(text="Помощь", callback_data="menu:help")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
