from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def notifications_keyboard(
    *,
    notify_new: bool,
    negative_only: bool,
    daily_digest: bool,
    notify_stale: bool,
    notify_questions: bool,
) -> InlineKeyboardMarkup:
    new_label = "🔔 Новые отзывы: вкл" if notify_new else "🔕 Новые отзывы: выкл"
    neg_label = "⚠️ Только негатив 1–3★: вкл" if negative_only else "⚠️ Только негатив: выкл"
    digest_label = "☀️ Утренний дайджест: вкл" if daily_digest else "🌙 Утренний дайджест: выкл"
    stale_label = (
        "⏳ Напоминание об очереди: вкл" if notify_stale else "⏳ Напоминание об очереди: выкл"
    )
    q_label = (
        "❓ Вопросы в кабинете: вкл" if notify_questions else "❓ Вопросы в кабинете: выкл"
    )
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=new_label, callback_data="settings:notify:toggle_new")],
            [InlineKeyboardButton(text=neg_label, callback_data="settings:notify:toggle_negative")],
            [InlineKeyboardButton(text=q_label, callback_data="settings:notify:toggle_questions")],
            [InlineKeyboardButton(text=digest_label, callback_data="settings:notify:toggle_digest")],
            [InlineKeyboardButton(text=stale_label, callback_data="settings:notify:toggle_stale")],
            [InlineKeyboardButton(text="⚙️ Настройки", callback_data="menu:settings")],
        ]
    )
