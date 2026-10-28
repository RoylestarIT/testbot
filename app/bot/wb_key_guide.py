"""Пошаговая инструкция API-ключа WB для бота «Голос бренда»."""

from __future__ import annotations

from pathlib import Path

from aiogram import Bot
from aiogram.types import (
    FSInputFile,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    Message,
)

from app.bot.ui import brand_title, bullet, muted, section

_ASSETS_DIR = Path(__file__).resolve().parent / "assets" / "wb_api_guide"

_BACK_CALLBACKS = {
    "connect": "settings:connect:wb",
    "onboard": "onboarding:step:0",
    "acc": "settings:accounts",
}

WB_SELLER_URL = "https://seller.wildberries.ru/"


def wb_key_guide_text() -> str:
    return (
        brand_title("Ключ Wildberries", tagline="7 шагов в кабинете продавца", icon="🟣")
        + section("Пошагово", icon="📋")
        + "\n"
        + bullet("1. Откройте кабинет продавца → меню профиля → <b>Настройки</b>")
        + "\n"
        + bullet('2. Вкладка <b>«Доступ к API»</b>')
        + "\n"
        + bullet("3. Придумайте имя ключа (например: «Ответы на отзывы»)")
        + "\n"
        + bullet('4. Категория API: <b>«Вопросы и отзывы»</b>')
        + "\n"
        + bullet("5. Нажмите <b>«Создать токен»</b>")
        + "\n"
        + bullet("6. Сразу нажмите <b>«Скопировать»</b> — токен показывают один раз")
        + "\n"
        + bullet("7. Вставьте ключ сюда в бот одним сообщением")
        + "\n\n"
        + muted(
            "Нужны только «Вопросы и отзывы». "
            "«Тестовый контур» включайте только для проверки, не для боевого магазина."
        )
        + "\n"
        + muted(f"Кабинет: {WB_SELLER_URL}")
    )


def _image_paths() -> list[Path]:
    names = ("wb_guide_step1.jpg", "wb_guide_step2.jpg", "wb_guide_step3.jpg")
    return [_ASSETS_DIR / name for name in names]


def wb_key_guide_keyboard(*, context: str = "acc") -> InlineKeyboardMarkup:
    ctx = context if context in _BACK_CALLBACKS else "acc"
    back_cb = _BACK_CALLBACKS[ctx]
    rows: list[list[InlineKeyboardButton]] = [
        [InlineKeyboardButton(text="🖼 Показать карточки", callback_data=f"help:wb_key:album:{ctx}")],
        [InlineKeyboardButton(text="🌐 Открыть кабинет WB", url=WB_SELLER_URL)],
    ]
    if ctx == "connect":
        rows.insert(0, [InlineKeyboardButton(text="✅ Готов — ввести ключ", callback_data="settings:connect:wb")])
    elif ctx == "onboard":
        rows.insert(
            0,
            [InlineKeyboardButton(text="⚙️ Открыть настройки", callback_data="menu:settings")],
        )
    rows.append([InlineKeyboardButton(text="◀️ Назад", callback_data=back_cb)])
    return InlineKeyboardMarkup(inline_keyboard=rows)


_ALBUM_CAPTIONS = (
    "🟣 <b>Шаг 1</b> — в меню профиля выберите «Настройки».",
    "🟣 <b>Шаги 2–5</b> — вкладка «Доступ к API», имя, «Вопросы и отзывы», «Создать токен».",
    "🟣 <b>Шаги 6–7</b> — «Скопировать» и вставить ключ в этот бот.",
)


async def send_wb_key_album(bot: Bot, chat_id: int) -> None:
    paths = _image_paths()
    missing = [p for p in paths if not p.is_file()]
    if missing:
        await bot.send_message(
            chat_id,
            muted("Карточки инструкции временно недоступны — пользуйтесь текстом выше."),
        )
        return
    media: list[InputMediaPhoto] = []
    for path, caption in zip(paths, _ALBUM_CAPTIONS, strict=True):
        media.append(InputMediaPhoto(media=FSInputFile(path), caption=caption, parse_mode="HTML"))
    await bot.send_media_group(chat_id, media)


def parse_wb_help_context(callback_data: str) -> tuple[str, str]:
    """Returns (action, context_key) — action: text|album, context: connect|onboard|acc."""
    parts = callback_data.split(":")
    if len(parts) >= 4 and parts[2] == "album":
        ctx = parts[3]
        return "album", ctx if ctx in _BACK_CALLBACKS else "acc"
    if len(parts) >= 3 and parts[2] in _BACK_CALLBACKS:
        return "text", parts[2]
    return "text", "acc"


async def send_wb_key_guide_message(message: Message, *, context: str = "acc") -> None:
    await message.answer(wb_key_guide_text(), reply_markup=wb_key_guide_keyboard(context=context))
