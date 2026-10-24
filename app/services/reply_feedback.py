from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

FEEDBACK_EVERY_N_ACTIONS = 5


def feedback_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="👍 Полезно", callback_data="feedback:up"),
                InlineKeyboardButton(text="👎 Не то", callback_data="feedback:down"),
            ],
            [InlineKeyboardButton(text="📬 Дальше", callback_data="review:mp:list")],
        ]
    )


def should_ask_feedback(action_count: int) -> bool:
    return action_count > 0 and action_count % FEEDBACK_EVERY_N_ACTIONS == 0
