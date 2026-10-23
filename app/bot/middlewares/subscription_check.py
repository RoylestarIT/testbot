from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, TelegramObject

from app.db.models import User
from app.services.generation_limit import can_generate, remaining_generations_today
from app.db.session import get_session_factory

GENERATION_CALLBACK_PREFIXES = (
    "review:tone:",
    "review:more",
)


class SubscriptionCheckMiddleware(BaseMiddleware):
    """Blocks LLM generation callbacks when Lite daily limit is exceeded."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if not isinstance(event, CallbackQuery) or not event.data:
            return await handler(event, data)

        if not any(event.data.startswith(prefix) for prefix in GENERATION_CALLBACK_PREFIXES):
            return await handler(event, data)

        user: User | None = data.get("user")
        if user is None:
            return await handler(event, data)

        session_factory = get_session_factory()
        async with session_factory() as session:
            allowed, message = await can_generate(session, user.id)
            remaining = await remaining_generations_today(session, user.id)
            data["generation_allowed"] = allowed
            data["generations_remaining"] = remaining

        if not allowed:
            await event.answer(message or "Лимит генераций исчерпан", show_alert=True)
            return None

        return await handler(event, data)
