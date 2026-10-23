from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def notifications_keyboard(*, notify_new: bool, negative_only: bool) -> InlineKeyboardMarkup:
    new_label = "🔔 Новые отзывы: вкл" if notify_new else "🔕 Новые отзывы: выкл"
    neg_label = "⚠️ Только негатив 1–3★: вкл" if negative_only else "⚠️ Только негатив: выкл"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=new_label, callback_data="settings:notify:toggle_new")],
            [InlineKeyboardButton(text=neg_label, callback_data="settings:notify:toggle_negative")],
            [InlineKeyboardButton(text="⚙️ Настройки", callback_data="menu:settings")],
        ]
    )
