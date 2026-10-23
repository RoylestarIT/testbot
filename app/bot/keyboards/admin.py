from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def admin_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📊 Статистика", callback_data="admin:stats")],
            [InlineKeyboardButton(text="⏳ Pending-заявки", callback_data="admin:pending:0")],
            [InlineKeyboardButton(text="🎁 Выдать подписку", callback_data="admin:grant")],
            [InlineKeyboardButton(text="📢 Рассылка", callback_data="admin:broadcast")],
            [InlineKeyboardButton(text="← Главное меню", callback_data="menu:main")],
        ]
    )


def admin_back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="← Админ-панель", callback_data="menu:admin")],
        ]
    )


def pending_detail_keyboard(subscription_id: int, index: int, total: int) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = [
        [
            InlineKeyboardButton(
                text="✅ Подтвердить",
                callback_data=f"admin:approve:{subscription_id}",
            ),
            InlineKeyboardButton(
                text="❌ Отклонить",
                callback_data=f"admin:reject:{subscription_id}",
            ),
        ],
    ]
    if total > 1:
        nav: list[InlineKeyboardButton] = []
        if index > 0:
            nav.append(
                InlineKeyboardButton(text="◀️", callback_data=f"admin:pending:{index - 1}")
            )
        nav.append(
            InlineKeyboardButton(text=f"{index + 1} / {total}", callback_data="admin:noop")
        )
        if index < total - 1:
            nav.append(
                InlineKeyboardButton(text="▶️", callback_data=f"admin:pending:{index + 1}")
            )
        rows.append(nav)
    rows.append([InlineKeyboardButton(text="← Админ-панель", callback_data="menu:admin")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def grant_cancel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Отмена", callback_data="admin:grant:cancel")],
        ]
    )


def grant_plan_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Lite", callback_data="admin:grant:plan:lite"),
                InlineKeyboardButton(text="PRO", callback_data="admin:grant:plan:pro"),
            ],
            [InlineKeyboardButton(text="Отмена", callback_data="admin:grant:cancel")],
        ]
    )


def broadcast_cancel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Отмена", callback_data="admin:broadcast:cancel")],
        ]
    )


def broadcast_preview_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Отправить всем",
                    callback_data="admin:broadcast:send",
                )
            ],
            [InlineKeyboardButton(text="Отмена", callback_data="admin:broadcast:cancel")],
        ]
    )
