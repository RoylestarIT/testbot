"""Пошаговая инструкция API-ключа WB для бота «Голос бренда»."""

from __future__ import annotations

from aiogram import Bot
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from app.bot.ui import brand_title, bullet, muted, section
from app.bot.utils.callbacks import safe_edit_message

_BACK_CALLBACKS = {
    "connect": "settings:accounts",
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
        + bullet("7. Вставьте ключ в этот чат <b>одним сообщением</b>")
        + "\n\n"
        + muted(
            "Достаточно доступа «Вопросы и отзывы». "
            "«Тестовый контур» — только для проверки, не для боевого магазина."
        )
    )


def wb_key_back_keyboard(*, context: str = "acc") -> InlineKeyboardMarkup:
    ctx = context if context in _BACK_CALLBACKS else "acc"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🌐 Открыть кабинет WB", url=WB_SELLER_URL)],
            [InlineKeyboardButton(text="◀️ Назад", callback_data=_BACK_CALLBACKS[ctx])],
        ]
    )


def parse_wb_help_context(callback_data: str) -> str:
    parts = callback_data.split(":")
    if len(parts) >= 3 and parts[2] in _BACK_CALLBACKS:
        return parts[2]
    return "acc"


async def deliver_wb_key_instruction(
    *,
    bot: Bot,
    chat_id: int,
    message: Message | None = None,
    context: str = "connect",
) -> None:
    body = wb_key_guide_text() + "\n\n" + "Когда ключ скопирован — <b>отправьте его сюда</b> одним сообщением."
    kb = wb_key_back_keyboard(context=context)
    if message is not None:
        await safe_edit_message(message, body, reply_markup=kb)
    else:
        await bot.send_message(chat_id, body, reply_markup=kb)


async def deliver_wb_key_instruction_callback(callback: CallbackQuery, *, context: str) -> None:
    if callback.message is None:
        return
    await deliver_wb_key_instruction(
        bot=callback.bot,
        chat_id=callback.message.chat.id,
        message=callback.message,
        context=context,
    )
