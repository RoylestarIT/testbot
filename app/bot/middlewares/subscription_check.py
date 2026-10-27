from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, TelegramObject

from app.db.models import User as DbUser
from app.db.session import get_session_factory
from app.services.generation_guard import can_start_generation, is_generation_callback
from app.services.generation_limit import remaining_generations_today


class GenerationGuardMiddleware(BaseMiddleware):
    """Блокирует LLM-генерацию: дневной лимит Free + почасовой лимит для всех."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if not isinstance(event, CallbackQuery) or not event.data:
            return await handler(event, data)

        if not is_generation_callback(event.data):
            return await handler(event, data)

        db_user: DbUser | None = data.get("db_user")
        if db_user is None:
            return await handler(event, data)

        session_factory = get_session_factory()
        async with session_factory() as session:
            allowed, message = await can_start_generation(session, db_user.id)
            remaining = await remaining_generations_today(session, db_user.id)
            data["generation_allowed"] = allowed
            data["generations_remaining"] = remaining

        if not allowed:
            await event.answer(message or "Лимит подготовки ответов исчерпан", show_alert=True)
            return None

        return await handler(event, data)


# Backward-compatible alias
SubscriptionCheckMiddleware = GenerationGuardMiddleware
