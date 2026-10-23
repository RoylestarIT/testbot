from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu_keyboard(*, show_admin: bool = False) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = [
        [InlineKeyboardButton(text="🏠 Сводка", callback_data="menu:dashboard")],
        [InlineKeyboardButton(text="Отзывы", callback_data="menu:reviews")],
        [
            InlineKeyboardButton(text="Настройки", callback_data="menu:settings"),
            InlineKeyboardButton(text="Подписка", callback_data="menu:subscription"),
        ],
        [InlineKeyboardButton(text="🆘 Поддержка", callback_data="menu:support")],
        [InlineKeyboardButton(text="Помощь", callback_data="menu:help")],
    ]
    if show_admin:
        rows.insert(4, [InlineKeyboardButton(text="🛠 Админ-панель", callback_data="menu:admin")])
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
        rows.append([InlineKeyboardButton(text="🎁 Trial PRO (7 дней)", callback_data="menu:trial_pro")])
    rows.extend(
        [
            [InlineKeyboardButton(text="📬 Новые отзывы", callback_data="review:mp:list")],
            [InlineKeyboardButton(text="🔄 Синхронизировать", callback_data="review:sync")],
            [InlineKeyboardButton(text="📋 Полное меню", callback_data="menu:full")],
        ]
    )
    if show_admin:
        rows.insert(-1, [InlineKeyboardButton(text="🛠 Админ", callback_data="menu:admin")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
