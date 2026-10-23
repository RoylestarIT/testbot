from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def admin_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📊 Статистика", callback_data="admin:stats")],
            [InlineKeyboardButton(text="⏳ Pending-платежи", callback_data="admin:pending")],
            [InlineKeyboardButton(text="📖 Команды", callback_data="admin:help")],
            [InlineKeyboardButton(text="← Главное меню", callback_data="menu:main")],
        ]
    )


def pending_subscription_keyboard(subscription_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Approve",
                    callback_data=f"admin:approve:{subscription_id}",
                ),
                InlineKeyboardButton(
                    text="❌ Reject",
                    callback_data=f"admin:reject:{subscription_id}",
                ),
            ],
        ]
    )
