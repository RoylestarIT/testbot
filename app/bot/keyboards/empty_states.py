from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.bot.keyboards.nav import nav_home_queue


def no_cabinets_keyboard() -> InlineKeyboardMarkup:
    return nav_home_queue(
        extra=[
            [InlineKeyboardButton(text="🟣 Подключить WB", callback_data="settings:connect:wb")],
            [InlineKeyboardButton(text="🔵 Подключить Ozon", callback_data="settings:connect:ozon")],
        ]
    )


def no_new_reviews_keyboard() -> InlineKeyboardMarkup:
    return nav_home_queue(
        extra=[
            [
                InlineKeyboardButton(text="🔄 Sync", callback_data="review:sync"),
                InlineKeyboardButton(text="⚙️ Настройки", callback_data="menu:settings"),
            ],
        ]
    )


def poller_notify_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📬  Очередь отзывов", callback_data="review:mp:list")],
            [InlineKeyboardButton(text="🏠  Сводка", callback_data="menu:dashboard")],
        ]
    )
