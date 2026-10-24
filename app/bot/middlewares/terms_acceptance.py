from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject, Update

from app.bot.copy import TERMS_TEXT
from app.bot.keyboards.terms import terms_acceptance_keyboard
from app.db.models import User as DbUser

_ACCEPT_CALLBACK = "onboarding:accept"


def _command_name(message: Message) -> str | None:
    text = (message.text or "").strip()
    if not text.startswith("/"):
        return None
    return text.split()[0].lstrip("/").split("@")[0].lower() or None


class TermsAcceptanceMiddleware(BaseMiddleware):
    """Не пускает в бот, пока пользователь не принял условия и политику."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        db_user: DbUser | None = data.get("db_user")
        if db_user is None or db_user.terms_accepted_at is not None:
            return await handler(event, data)

        if isinstance(event, Update):
            if event.callback_query is not None:
                return await self._gate_callback(event.callback_query, handler, event, data)
            if event.message is not None:
                return await self._gate_message(event.message, handler, event, data)
            return await handler(event, data)

        if isinstance(event, CallbackQuery) or (
            getattr(event, "data", None) is not None and callable(getattr(event, "answer", None))
        ):
            return await self._gate_callback(event, handler, event, data)
        if isinstance(event, Message) or getattr(event, "text", None) is not None:
            return await self._gate_message(event, handler, event, data)
        return await handler(event, data)

    async def _gate_callback(
        self,
        callback: CallbackQuery,
        handler: Callable[..., Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if callback.data == _ACCEPT_CALLBACK:
            return await handler(event, data)
        if callback.data and callback.data.startswith("legal:"):
            return await handler(event, data)
        await callback.answer("Сначала примите условия использования.", show_alert=True)
        if callback.message is not None:
            await callback.message.answer(TERMS_TEXT, reply_markup=terms_acceptance_keyboard())
        return None

    async def _gate_message(
        self,
        message: Message,
        handler: Callable[..., Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if _command_name(message) == "start":
            return await handler(event, data)
        await message.answer(TERMS_TEXT, reply_markup=terms_acceptance_keyboard())
        return None
