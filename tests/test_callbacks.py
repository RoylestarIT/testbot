from unittest.mock import AsyncMock, MagicMock

import pytest
from aiogram.exceptions import TelegramBadRequest

from app.bot.utils.callbacks import safe_edit_message


@pytest.mark.asyncio
async def test_safe_edit_deletes_and_resends_on_bad_request() -> None:
    message = MagicMock()
    message.edit_text = AsyncMock(
        side_effect=TelegramBadRequest(method=None, message="there is no text in the message to edit")
    )
    message.delete = AsyncMock()
    message.answer = AsyncMock()

    await safe_edit_message(message, "Новый экран", reply_markup=None)

    message.delete.assert_awaited_once()
    message.answer.assert_awaited_once_with("Новый экран", reply_markup=None)
