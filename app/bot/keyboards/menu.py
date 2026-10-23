from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.bot.keyboards.nav import nav_home_queue


def main_menu_keyboard(*, show_admin: bool = False) -> InlineKeyboardMarkup:
    """Компактное меню (справка, поддержка, редкие разделы)."""
    rows: list[list[InlineKeyboardButton]] = [
        [
            InlineKeyboardButton(text="📬 Очередь", callback_data="review:mp:list"),
            InlineKeyboardButton(text="🔄 Sync", callback_data="review:sync"),
        ],
        [
            InlineKeyboardButton(text="⚙️ Настройки", callback_data="menu:settings"),
            InlineKeyboardButton(text="💎 Подписка", callback_data="menu:subscription"),
        ],
        [
            InlineKeyboardButton(text="✍️ Ручной ответ", callback_data="review:manual:start"),
            InlineKeyboardButton(text="📚 История", callback_data="review:history"),
        ],
        [
            InlineKeyboardButton(text="🆘 Поддержка", callback_data="menu:support"),
            InlineKeyboardButton(text="📖 Справка", callback_data="menu:help"),
        ],
    ]
    if show_admin:
        rows.insert(2, [InlineKeyboardButton(text="🛠 Админ", callback_data="menu:admin")])
    rows.append([InlineKeyboardButton(text="🏠 Сводка", callback_data="menu:dashboard")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def dashboard_keyboard(
    *,
    show_trial: bool,
    show_onboarding: bool,
    show_admin: bool,
) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    if show_onboarding:
        rows.append([InlineKeyboardButton(text="🚀 Начать настройку", callback_data="menu:onboarding")])
    if show_trial:
        rows.append([InlineKeyboardButton(text="🎁 Trial PRO · 7 дней", callback_data="menu:trial_pro")])

    rows.extend(
        [
            [InlineKeyboardButton(text="📬  Ответить на отзывы", callback_data="review:mp:list")],
            [
                InlineKeyboardButton(text="🔄 Sync", callback_data="review:sync"),
                InlineKeyboardButton(text="📚 История", callback_data="review:history"),
            ],
            [
                InlineKeyboardButton(text="⚙️ Настройки", callback_data="menu:settings"),
                InlineKeyboardButton(text="💎 Подписка", callback_data="menu:subscription"),
            ],
            [
                InlineKeyboardButton(text="📊 Подробнее", callback_data="menu:dashboard:details"),
                InlineKeyboardButton(text="⋯ Ещё", callback_data="menu:more"),
            ],
        ]
    )
    if show_admin:
        rows.insert(-1, [InlineKeyboardButton(text="🛠 Админ", callback_data="menu:admin")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
