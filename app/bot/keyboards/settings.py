from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.db.models import Marketplace, MarketplaceAccount, ToneProfile


def settings_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Кабинеты маркетплейсов", callback_data="settings:accounts")],
            [InlineKeyboardButton(text="Tone of voice", callback_data="settings:tone")],
            [
                InlineKeyboardButton(
                    text="Авто-публикация ответов (PRO)",
                    callback_data="pro:autopublish",
                ),
            ],
            [InlineKeyboardButton(text="← Главное меню", callback_data="menu:main")],
        ]
    )


def accounts_menu_keyboard(accounts: list[MarketplaceAccount]) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for acc in accounts:
        mp = "WB" if acc.marketplace == Marketplace.WB else "Ozon"
        name = acc.shop_name or f"{mp} #{acc.id}"
        status = "✅" if acc.is_active else "⏸"
        rows.append(
            [
                InlineKeyboardButton(
                    text=f"{status} {name}",
                    callback_data=f"settings:account:{acc.id}",
                )
            ]
        )
    rows.extend(
        [
            [InlineKeyboardButton(text="+ Wildberries", callback_data="settings:connect:wb")],
            [InlineKeyboardButton(text="+ Ozon", callback_data="settings:connect:ozon")],
            [InlineKeyboardButton(text="← Настройки", callback_data="menu:settings")],
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def account_detail_keyboard(account_id: int, is_active: bool) -> InlineKeyboardMarkup:
    toggle = "Отключить" if is_active else "Включить"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=toggle,
                    callback_data=f"settings:account_toggle:{account_id}",
                )
            ],
            [InlineKeyboardButton(text="← Кабинеты", callback_data="settings:accounts")],
        ]
    )


def tone_menu_keyboard(profiles: list[ToneProfile]) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for profile in profiles:
        label = (profile.description or f"Профиль #{profile.id}")[:48]
        rows.append(
            [
                InlineKeyboardButton(
                    text=label,
                    callback_data=f"settings:tone:view:{profile.id}",
                )
            ]
        )
    rows.extend(
        [
            [InlineKeyboardButton(text="+ Новый профиль", callback_data="settings:tone:add")],
            [InlineKeyboardButton(text="← Настройки", callback_data="menu:settings")],
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def tone_detail_keyboard(profile_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Удалить",
                    callback_data=f"settings:tone:delete:{profile_id}",
                )
            ],
            [InlineKeyboardButton(text="← Tone of voice", callback_data="settings:tone")],
        ]
    )
