from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def no_cabinets_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="→  Подключить WB", callback_data="settings:connect:wb")],
            [InlineKeyboardButton(text="→  Подключить Ozon", callback_data="settings:connect:ozon")],
            [InlineKeyboardButton(text="←  Отзывы", callback_data="menu:reviews")],
        ]
    )


def no_new_reviews_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="→  Синхронизация", callback_data="review:sync")],
            [InlineKeyboardButton(text="→  Настройки", callback_data="menu:settings")],
            [InlineKeyboardButton(text="←  Отзывы", callback_data="menu:reviews")],
        ]
    )


def poller_notify_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="→  Очередь отзывов", callback_data="review:mp:list")],
            [InlineKeyboardButton(text="→  Сводка", callback_data="menu:dashboard")],
        ]
    )
