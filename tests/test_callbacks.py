from unittest.mock import AsyncMock, MagicMock

import pytest
from aiogram.exceptions import TelegramBadRequest

from app.bot.utils.callbacks import safe_edit_message, safe_edit_message_by_id


@pytest.mark.asyncio
async def test_safe_edit_deletes_and_resends_on_bad_request() -> None:
    message = MagicMock()
    message.chat.id = 1
    message.message_id = 42
    message.bot = MagicMock()
    message.bot.edit_message_text = AsyncMock(
        side_effect=TelegramBadRequest(method=None, message="there is no text in the message to edit")
    )
    message.bot.edit_message_caption = AsyncMock(
        side_effect=TelegramBadRequest(method=None, message="message not found")
    )
    message.bot.delete_message = AsyncMock()
    message.bot.send_message = AsyncMock()

    await safe_edit_message(message, "Новый экран", reply_markup=None)

    message.bot.delete_message.assert_awaited_once_with(1, 42)
    message.bot.send_message.assert_awaited_once_with(1, "Новый экран", reply_markup=None)


@pytest.mark.asyncio
async def test_safe_edit_uses_caption_when_no_text() -> None:
    bot = MagicMock()
    bot.edit_message_text = AsyncMock(
        side_effect=TelegramBadRequest(method=None, message="there is no text in the message to edit")
    )
    bot.edit_message_caption = AsyncMock()

    await safe_edit_message_by_id(bot, 10, 5, "Подпись", reply_markup=None)

    bot.edit_message_caption.assert_awaited_once()
    bot.edit_message_text.assert_awaited_once()
