from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, TelegramObject

from app.db.models import User as DbUser
from app.db.session import get_session_factory
from app.services.generation_limit import is_pro_user

PRO_CALLBACK_PREFIX = "pro:"


class ProSubscriptionMiddleware(BaseMiddleware):
    """Allows only users with an active PRO subscription."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if not isinstance(event, CallbackQuery) or not event.data:
            return await handler(event, data)
        if not event.data.startswith(PRO_CALLBACK_PREFIX):
            return await handler(event, data)

        db_user: DbUser | None = data.get("db_user")
        if db_user is None:
            await event.answer("Сначала отправьте /start", show_alert=True)
            return None

        session_factory = get_session_factory()
        async with session_factory() as session:
            allowed = await is_pro_user(session, db_user.id)

        if not allowed:
            await event.answer(
                "PRO (1 600 ₽): publish в API и авто только на 4–5★. "
                "Lite — генерация и копирование. Негатив всегда вручную. "
                "«Подписка» → Сравнение тарифов.",
                show_alert=True,
            )
            return None

        return await handler(event, data)
