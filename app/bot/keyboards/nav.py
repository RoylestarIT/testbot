"""Единая навигация — меньше «вкладок», всегда понятный выход домой и в ответы."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.bot.ui import REVIEWS_HUB_BUTTON


def nav_home_queue(*, extra: list[list[InlineKeyboardButton]] | None = None) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = list(extra or [])
    rows.append(
        [
            InlineKeyboardButton(text="🏠 Сводка", callback_data="menu:dashboard"),
            InlineKeyboardButton(text=REVIEWS_HUB_BUTTON, callback_data="review:mp:list"),
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def nav_home_settings() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🏠 Сводка", callback_data="menu:dashboard"),
                InlineKeyboardButton(text="⚙️ Настройки", callback_data="menu:settings"),
            ],
        ]
    )


def after_review_action_keyboard(*, has_next: bool = False, upsell: bool = False) -> InlineKeyboardMarkup:
    extra: list[list[InlineKeyboardButton]] = []
    if upsell:
        extra.append([InlineKeyboardButton(text="💎 Подписка", callback_data="menu:subscription")])
    if has_next:
        extra.append([InlineKeyboardButton(text="➡️ Следующий", callback_data="review:mp:next")])
    return nav_home_queue(extra=extra)
