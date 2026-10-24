from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from aiogram.types import CallbackQuery

from app.bot.middlewares.terms_acceptance import TermsAcceptanceMiddleware
from app.db.models import User


@pytest.mark.asyncio
async def test_terms_middleware_blocks_callback_until_accepted() -> None:
    mw = TermsAcceptanceMiddleware()
    handler = AsyncMock(return_value="ok")
    user = User(id=1, tg_id=1, terms_accepted_at=None)
    callback = MagicMock(spec=CallbackQuery)
    callback.data = "menu:subscription"
    callback.answer = AsyncMock()
    callback.message = MagicMock()
    callback.message.answer = AsyncMock()

    result = await mw(handler, callback, {"db_user": user})

    assert result is None
    handler.assert_not_called()
    callback.answer.assert_called_once()


@pytest.mark.asyncio
async def test_terms_middleware_allows_accept_callback() -> None:
    mw = TermsAcceptanceMiddleware()
    handler = AsyncMock(return_value="ok")
    user = User(id=1, tg_id=1, terms_accepted_at=None)
    callback = MagicMock(spec=CallbackQuery)
    callback.data = "onboarding:accept"

    result = await mw(handler, callback, {"db_user": user})

    assert result == "ok"
    handler.assert_called_once()


@pytest.mark.asyncio
async def test_terms_middleware_passes_when_already_accepted() -> None:
    mw = TermsAcceptanceMiddleware()
    handler = AsyncMock(return_value="ok")
    user = User(id=1, tg_id=1, terms_accepted_at=datetime.now(UTC))
    callback = MagicMock(spec=CallbackQuery)
    callback.data = "menu:dashboard"

    result = await mw(handler, callback, {"db_user": user})

    assert result == "ok"
    handler.assert_called_once()
