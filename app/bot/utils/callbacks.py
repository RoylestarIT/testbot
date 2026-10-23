from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message


async def _delete_message_quiet(message: Message) -> None:
    try:
        await message.delete()
    except TelegramBadRequest:
        pass


async def safe_edit_message(
    message: Message,
    text: str,
    *,
    reply_markup: InlineKeyboardMarkup | None = None,
    replace_on_fail: bool = True,
) -> None:
    """Меняет текст inline-сообщения; при ошибке — удаляет старое и шлёт новое (без «стопки»)."""
    try:
        await message.edit_text(text, reply_markup=reply_markup)
    except TelegramBadRequest as exc:
        err = str(exc).lower()
        if "message is not modified" in err:
            return
        if not replace_on_fail:
            await message.answer(text, reply_markup=reply_markup)
            return
        await _delete_message_quiet(message)
        await message.answer(text, reply_markup=reply_markup)


async def answer_and_edit(
    callback: CallbackQuery,
    text: str,
    *,
    reply_markup: InlineKeyboardMarkup | None = None,
    alert: str | None = None,
) -> None:
    if alert:
        await callback.answer(alert)
    else:
        await callback.answer()
    if callback.message is None:
        return
    await safe_edit_message(callback.message, text, reply_markup=reply_markup)
