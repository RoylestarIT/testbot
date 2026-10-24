from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.bot.ui import REVIEWS_HUB_BUTTON
from app.core.config import get_settings


def more_menu_keyboard(*, show_admin: bool = False) -> InlineKeyboardMarkup:
    """«⋯ Ещё» — только справка и поддержка, без дубля сводки."""
    rows: list[list[InlineKeyboardButton]] = [
        [
            InlineKeyboardButton(text="🆘 Поддержка", callback_data="menu:support"),
            InlineKeyboardButton(text="📖 Справка", callback_data="menu:help"),
        ],
        [
            InlineKeyboardButton(text="🩺 Здоровье", callback_data="menu:service_status"),
            InlineKeyboardButton(text="📜 Обновления", callback_data="menu:changelog"),
        ],
        [InlineKeyboardButton(text="📜 Документы", callback_data="menu:legal")],
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
    show_product_news: bool = False,
) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    if show_onboarding:
        rows.append([InlineKeyboardButton(text="🚀 Начать настройку", callback_data="menu:onboarding")])
    if show_trial:
        days = get_settings().trial_pro_days
        rows.append(
            [InlineKeyboardButton(text=f"🎁 Trial PRO · {days} дн.", callback_data="menu:trial_pro")]
        )
    if show_product_news:
        rows.append(
            [
                InlineKeyboardButton(text="✓ Понятно", callback_data="news:dismiss"),
                InlineKeyboardButton(text="📜 Документы", callback_data="menu:legal"),
            ]
        )

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
                InlineKeyboardButton(text="🩺 Здоровье", callback_data="menu:service_status"),
            ],
            [
                InlineKeyboardButton(text="ℹ️ Почему мы", callback_data="menu:why_us"),
                InlineKeyboardButton(text="❓ Вопросы WB", callback_data="menu:wb_questions"),
            ],
            [InlineKeyboardButton(text="⋯ Ещё", callback_data="menu:more")],
        ]
    )
    if show_admin:
        rows.insert(-1, [InlineKeyboardButton(text="🛠 Админ", callback_data="menu:admin")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
