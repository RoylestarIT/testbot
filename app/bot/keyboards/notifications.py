from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def notifications_keyboard(
    *,
    notify_new: bool,
    negative_only: bool,
    daily_digest: bool,
) -> InlineKeyboardMarkup:
    new_label = "🔔 Новые отзывы: вкл" if notify_new else "🔕 Новые отзывы: выкл"
    neg_label = "⚠️ Только негатив 1–3★: вкл" if negative_only else "⚠️ Только негатив: выкл"
    digest_label = "☀️ Утренний дайджест: вкл" if daily_digest else "🌙 Утренний дайджест: выкл"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=new_label, callback_data="settings:notify:toggle_new")],
            [InlineKeyboardButton(text=neg_label, callback_data="settings:notify:toggle_negative")],
            [InlineKeyboardButton(text=digest_label, callback_data="settings:notify:toggle_digest")],
            [InlineKeyboardButton(text="⚙️ Настройки", callback_data="menu:settings")],
        ]
    )
