"""Тексты и клавиатура поддержки (без импорта handlers — избегаем циклов)."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.bot.keyboards.legal import legal_open_from_terms_row
from app.bot.keyboards.nav import nav_back_more
from app.bot.ui import brand_title, muted, section
from app.core.config import get_settings


def support_screen_text() -> str:
    settings = get_settings()
    contact = (
        f"@{settings.support_username.lstrip('@')}"
        if settings.support_username
        else "администратору проекта"
    )
    return (
        brand_title(
            "Поддержка",
            tagline="Кабинеты WB/Ozon, оплата и ответы на отзывы — в Telegram",
            icon="🆘",
        )
        + section("Контакт", icon="💬")
        + f"\n  <b>{contact}</b>\n"
        + muted("Опишите проблему одним сообщением в личку.")
    )


def support_keyboard() -> InlineKeyboardMarkup:
    settings = get_settings()
    rows: list[list[InlineKeyboardButton]] = []
    if settings.support_username:
        uname = settings.support_username.lstrip("@")
        rows.append(
            [InlineKeyboardButton(text="💬 Написать в поддержку", url=f"https://t.me/{uname}")]
        )
    rows.append([InlineKeyboardButton(text="✉️ Написать из бота", callback_data="support:write")])
    rows.append(legal_open_from_terms_row(back="s"))
    rows.extend(nav_back_more().inline_keyboard)
    return InlineKeyboardMarkup(inline_keyboard=rows)
