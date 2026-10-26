from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message


async def _delete_message_quiet(message: Message) -> None:
    try:
        await message.delete()
    except TelegramBadRequest:
        pass


async def _delete_message_id_quiet(bot: Bot, chat_id: int, message_id: int) -> None:
    try:
        await bot.delete_message(chat_id, message_id)
    except TelegramBadRequest:
        pass


def _is_not_modified(exc: TelegramBadRequest) -> bool:
    return "message is not modified" in str(exc).lower()


def _no_text_to_edit(exc: TelegramBadRequest) -> bool:
    err = str(exc).lower()
    return "there is no text in the message to edit" in err or "message doesn't contain text" in err


async def safe_edit_message_by_id(
    bot: Bot,
    chat_id: int,
    message_id: int,
    text: str,
    *,
    reply_markup: InlineKeyboardMarkup | None = None,
    replace_on_fail: bool = True,
) -> None:
    """Редактирует сообщение по id; при ошибке — caption или (опционально) новое сообщение."""
    try:
        await bot.edit_message_text(
            text,
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=reply_markup,
        )
    except TelegramBadRequest as exc:
        if _is_not_modified(exc):
            return
        if _no_text_to_edit(exc):
            try:
                await bot.edit_message_caption(
                    caption=text,
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=reply_markup,
                )
                return
            except TelegramBadRequest as cap_exc:
                if _is_not_modified(cap_exc):
                    return
                exc = cap_exc
        if not replace_on_fail:
            await bot.send_message(chat_id, text, reply_markup=reply_markup)
            return
        await _delete_message_id_quiet(bot, chat_id, message_id)
        await bot.send_message(chat_id, text, reply_markup=reply_markup)


async def safe_edit_message(
    message: Message,
    text: str,
    *,
    reply_markup: InlineKeyboardMarkup | None = None,
    replace_on_fail: bool = True,
) -> None:
    """Меняет текст inline-сообщения; при ошибке — caption или удаление + новое (крайний случай)."""
    if message.chat is None:
        return
    await safe_edit_message_by_id(
        message.bot,
        message.chat.id,
        message.message_id,
        text,
        reply_markup=reply_markup,
        replace_on_fail=replace_on_fail,
    )


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
