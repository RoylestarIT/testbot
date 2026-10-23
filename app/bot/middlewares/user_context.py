from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from app.core.config import get_settings
from app.db.models import User
from app.db.repositories.user import UserRepository
from app.db.session import get_session_factory


class UserContextMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        tg_user = None
        if isinstance(event, Message) and event.from_user:
            tg_user = event.from_user
        elif isinstance(event, CallbackQuery) and event.from_user:
            tg_user = event.from_user

        if tg_user is None:
            return await handler(event, data)

        settings = get_settings()
        is_admin = tg_user.id in settings.admin_ids

        session_factory = get_session_factory()
        async with session_factory() as session:
            repo = UserRepository(session)
            user, _created = await repo.get_or_create(
                tg_id=tg_user.id,
                username=tg_user.username,
                is_admin=is_admin,
            )
            await session.commit()
            data["user"] = user
            data["db_user"] = user

        return await handler(event, data)
