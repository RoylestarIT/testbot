from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.db.models import Marketplace, MarketplaceAccount, ToneProfile


def settings_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🏪  Кабинеты WB/Ozon", callback_data="settings:accounts")],
            [InlineKeyboardButton(text="🎨  Tone of voice", callback_data="settings:tone")],
            [InlineKeyboardButton(text="🔔  Уведомления", callback_data="settings:notifications")],
            [
                InlineKeyboardButton(
                    text="🚀  Авто-публикация (PRO)",
                    callback_data="pro:autopublish",
                ),
            ],
            [InlineKeyboardButton(text="🏠  Сводка", callback_data="menu:main")],
        ]
    )


def accounts_menu_keyboard(accounts: list[MarketplaceAccount]) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for acc in accounts:
        mp = "🟣" if acc.marketplace == Marketplace.WB else "🔵"
        name = acc.shop_name or f"#{acc.id}"
        status = "✅" if acc.is_active else "⏸"
        rows.append(
            [
                InlineKeyboardButton(
                    text=f"{status} {mp} {name}",
                    callback_data=f"settings:account:{acc.id}",
                )
            ]
        )
    rows.extend(
        [
            [InlineKeyboardButton(text="➕ Wildberries", callback_data="settings:connect:wb")],
            [InlineKeyboardButton(text="➕ Ozon", callback_data="settings:connect:ozon")],
            [InlineKeyboardButton(text="⚙️ Настройки", callback_data="menu:settings")],
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def account_detail_keyboard(
    account_id: int,
    is_active: bool,
    *,
    auto_publish_enabled: bool = False,
    show_auto_publish: bool = False,
) -> InlineKeyboardMarkup:
    toggle = "⏸ Отключить" if is_active else "▶️ Включить"
    rows: list[list[InlineKeyboardButton]] = [
        [
            InlineKeyboardButton(
                text=toggle,
                callback_data=f"settings:account_toggle:{account_id}",
            )
        ],
    ]
    if show_auto_publish:
        ap_label = "🔴 Выкл авто-публикацию" if auto_publish_enabled else "🟢 Вкл авто-публикацию (4–5★)"
        rows.append(
            [
                InlineKeyboardButton(
                    text=ap_label,
                    callback_data=f"settings:account_autopublish:{account_id}",
                )
            ]
        )
    rows.append([InlineKeyboardButton(text="🏪 Кабинеты", callback_data="settings:accounts")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def autopublish_accounts_keyboard(accounts: list[MarketplaceAccount]) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for acc in accounts:
        if acc.marketplace not in (Marketplace.WB, Marketplace.OZON):
            continue
        mp = "🟣" if acc.marketplace == Marketplace.WB else "🔵"
        name = acc.shop_name or f"#{acc.id}"
        flag = "✅" if acc.auto_publish_enabled else "⬜"
        rows.append(
            [
                InlineKeyboardButton(
                    text=f"{flag} {mp} {name}",
                    callback_data=f"settings:account_autopublish:{acc.id}",
                )
            ]
        )
    rows.append([InlineKeyboardButton(text="⚙️ Настройки", callback_data="menu:settings")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def sync_accounts_keyboard(accounts: list[MarketplaceAccount]) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for acc in accounts:
        mp = "🟣" if acc.marketplace == Marketplace.WB else "🔵"
        name = acc.shop_name or f"#{acc.id}"
        rows.append(
            [
                InlineKeyboardButton(
                    text=f"{mp} {name}",
                    callback_data=f"review:sync:{acc.id}",
                )
            ]
        )
    rows.extend(
        [
            [InlineKeyboardButton(text="🔄 Все кабинеты", callback_data="review:sync:all")],
            [InlineKeyboardButton(text="💬 Отзывы", callback_data="menu:reviews")],
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def tone_menu_keyboard(profiles: list[ToneProfile]) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for profile in profiles:
        prefix = "⭐ " if profile.is_default else "🎨 "
        label = (profile.description or f"Профиль #{profile.id}")[:46]
        rows.append(
            [
                InlineKeyboardButton(
                    text=f"{prefix}{label}",
                    callback_data=f"settings:tone:view:{profile.id}",
                )
            ]
        )
    rows.extend(
        [
            [InlineKeyboardButton(text="➕ Новый профиль", callback_data="settings:tone:add")],
            [InlineKeyboardButton(text="⚙️ Настройки", callback_data="menu:settings")],
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def tone_detail_keyboard(profile_id: int, is_default: bool) -> InlineKeyboardMarkup:
    default_btn = (
        "⭐ Уже по умолчанию"
        if is_default
        else "⭐ Сделать по умолчанию"
    )
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✏️ Редактировать",
                    callback_data=f"settings:tone:edit:{profile_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text=default_btn,
                    callback_data=f"settings:tone:default:{profile_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🗑 Удалить",
                    callback_data=f"settings:tone:delete:{profile_id}",
                )
            ],
            [InlineKeyboardButton(text="🎨 Tone of voice", callback_data="settings:tone")],
        ]
    )
