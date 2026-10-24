from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.db.models import MarketplaceAccount


def autopublish_detail_keyboard(account: MarketplaceAccount) -> InlineKeyboardMarkup:
    min_r = account.auto_publish_min_rating or 4
    rule_label = "⭐ Правило: только 5★" if min_r >= 5 else "⭐ Правило: 4–5★"
    empty_label = (
        "📝 Только ★ без текста: вкл"
        if account.auto_publish_stars_only
        else "📝 Только ★ без текста: выкл"
    )
    stops = (account.auto_publish_stop_words or "").strip()
    stop_label = "🚫 Стоп-слова: заданы" if stops else "🚫 Стоп-слова"
    ap_label = "🔴 Выключить авто" if account.auto_publish_enabled else "🟢 Включить авто"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=ap_label, callback_data=f"settings:account_autopublish:{account.id}")],
            [InlineKeyboardButton(text=rule_label, callback_data=f"settings:autopublish_min:{account.id}")],
            [InlineKeyboardButton(text=empty_label, callback_data=f"settings:autopublish_empty:{account.id}")],
            [InlineKeyboardButton(text=stop_label, callback_data=f"settings:autopublish_stops:{account.id}")],
            [InlineKeyboardButton(text="◀️ Авто-публикация", callback_data="pro:autopublish")],
        ]
    )
