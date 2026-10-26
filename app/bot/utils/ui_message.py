"""Редактирование одного «экранного» сообщения в FSM (без стопки снизу)."""

from __future__ import annotations

from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, Message

from app.bot.utils.callbacks import _delete_message_quiet, safe_edit_message_by_id

UI_MESSAGE_ID_KEY = "ui_message_id"


async def bind_ui_message(state: FSMContext, message: Message | None) -> None:
    if message is not None:
        await state.update_data(**{UI_MESSAGE_ID_KEY: message.message_id})


async def edit_bound_ui_message(
    message: Message,
    state: FSMContext,
    text: str,
    *,
    reply_markup: InlineKeyboardMarkup | None = None,
    delete_user_message: bool = False,
) -> None:
    """Меняет текст привязанного inline-сообщения; иначе — обычный answer."""
    data = await state.get_data()
    ui_id = data.get(UI_MESSAGE_ID_KEY)
    if ui_id is not None and message.chat is not None:
        await safe_edit_message_by_id(
            message.bot,
            message.chat.id,
            int(ui_id),
            text,
            reply_markup=reply_markup,
        )
        if delete_user_message:
            await _delete_message_quiet(message)
        return
    await message.answer(text, reply_markup=reply_markup)
