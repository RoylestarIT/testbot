from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.dispatcher.middlewares.user_context import EVENT_FROM_USER_KEY
from aiogram.types import CallbackQuery, Message, TelegramObject, Update
from loguru import logger

from app.core.config import get_settings
from app.db.repositories.user import UserRepository
from app.db.session import get_session_factory


def _resolve_telegram_user(event: TelegramObject, data: dict[str, Any]):
    tg_user = data.get(EVENT_FROM_USER_KEY)
    if tg_user is not None:
        return tg_user
    if isinstance(event, Update):
        if event.callback_query and event.callback_query.from_user:
            return event.callback_query.from_user
        if event.message and event.message.from_user:
            return event.message.from_user
        if event.pre_checkout_query and event.pre_checkout_query.from_user:
            return event.pre_checkout_query.from_user
    if isinstance(event, Message) and event.from_user:
        return event.from_user
    if isinstance(event, CallbackQuery) and event.from_user:
        return event.from_user
    return None


class UserContextMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        tg_user = _resolve_telegram_user(event, data)
        if tg_user is None:
            return await handler(event, data)

        settings = get_settings()
        is_admin = tg_user.id in settings.admin_ids

        try:
            session_factory = get_session_factory()
            async with session_factory() as session:
                repo = UserRepository(session)
                db_user, _created = await repo.get_or_create(
                    tg_id=tg_user.id,
                    username=tg_user.username,
                    is_admin=is_admin,
                )
                await session.commit()
        except Exception:
            # The user-facing hint is sent by the global dp.errors() handler.
            logger.exception("Failed to load DB user for tg_id={}", tg_user.id)
            raise

        data["db_user"] = db_user
        return await handler(event, data)
