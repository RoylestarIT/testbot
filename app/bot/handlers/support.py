from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from app.bot.keyboards.menu import main_menu_keyboard
from app.core.config import get_settings

router = Router(name="support")


def support_keyboard() -> InlineKeyboardMarkup:
    settings = get_settings()
    rows: list[list[InlineKeyboardButton]] = []
    if settings.support_username:
        uname = settings.support_username.lstrip("@")
        rows.append(
            [InlineKeyboardButton(text="💬 Написать в поддержку", url=f"https://t.me/{uname}")]
        )
    rows.append([InlineKeyboardButton(text="🏠 Главное меню", callback_data="menu:main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


@router.callback_query(F.data == "menu:support")
async def menu_support(callback: CallbackQuery) -> None:
    settings = get_settings()
    await callback.answer()
    contact = f"@{settings.support_username.lstrip('@')}" if settings.support_username else "администратору проекта"
    from app.bot.ui import brand_title, muted, section

    text = (
        brand_title("Поддержка", tagline="Поможем с API, оплатой и генерацией", icon="🆘")
        + section("Контакт", icon="💬")
        + f"\n  <b>{contact}</b>\n"
        + muted("Опишите проблему одним сообщением в личку.")
    )
    if callback.message:
        await callback.message.edit_text(text, reply_markup=support_keyboard())
