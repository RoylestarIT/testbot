from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.bot.ui import REVIEWS_HUB_BUTTON


def more_menu_keyboard(*, show_admin: bool = False) -> InlineKeyboardMarkup:
    """«⋯ Ещё» — только справка и поддержка, без дубля сводки."""
    rows: list[list[InlineKeyboardButton]] = [
        [
            InlineKeyboardButton(text="🆘 Поддержка", callback_data="menu:support"),
            InlineKeyboardButton(text="📖 Справка", callback_data="menu:help"),
        ],
        [InlineKeyboardButton(text="🏠 Сводка", callback_data="menu:dashboard")],
    ]
    if show_admin:
        rows.insert(1, [InlineKeyboardButton(text="🛠 Админ", callback_data="menu:admin")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def main_menu_keyboard(*, show_admin: bool = False) -> InlineKeyboardMarkup:
    """Низ экранов (help, promo): ответы + сводка + справка."""
    rows: list[list[InlineKeyboardButton]] = [
        [InlineKeyboardButton(text=REVIEWS_HUB_BUTTON, callback_data="review:mp:list")],
        [
            InlineKeyboardButton(text="🆘 Поддержка", callback_data="menu:support"),
            InlineKeyboardButton(text="📖 Справка", callback_data="menu:help"),
        ],
        [InlineKeyboardButton(text="🏠 Сводка", callback_data="menu:dashboard")],
    ]
    if show_admin:
        rows.insert(2, [InlineKeyboardButton(text="🛠 Админ", callback_data="menu:admin")])
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
            [InlineKeyboardButton(text=REVIEWS_HUB_BUTTON, callback_data="review:mp:list")],
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
                InlineKeyboardButton(text="ℹ️ Почему мы", callback_data="menu:why_us"),
            ],
            [InlineKeyboardButton(text="⋯ Ещё", callback_data="menu:more")],
        ]
    )
    if show_admin:
        rows.insert(-1, [InlineKeyboardButton(text="🛠 Админ", callback_data="menu:admin")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
