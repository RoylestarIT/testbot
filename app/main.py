import asyncio

from aiogram import Bot, Dispatcher
from aiogram.types import ErrorEvent
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from aiogram.fsm.storage.memory import MemoryStorage
from loguru import logger

from app.bot.handlers import main_router
from app.bot.middlewares.user_context import UserContextMiddleware
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.db.session import close_db, init_db
from app.services.marketplace.http_pool import close_marketplace_http_clients
from app.tasks.poller import marketplace_poller_loop

_poller_task: asyncio.Task[None] | None = None


async def _register_bot_commands(bot: Bot) -> None:
    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Главное меню"),
            BotCommand(command="dashboard", description="Сводка и статусы"),
            BotCommand(command="my_subscription", description="Моя подписка"),
            BotCommand(command="admin", description="Админ-панель"),
        ]
    )


async def on_startup(bot: Bot) -> None:
    global _poller_task
    await init_db()
    logger.info("Database initialized")
    await _register_bot_commands(bot)
    _poller_task = asyncio.create_task(marketplace_poller_loop(bot))


async def on_shutdown(*_args: object, **_kwargs: object) -> None:
    global _poller_task
    if _poller_task is not None:
        _poller_task.cancel()
        try:
            await _poller_task
        except asyncio.CancelledError:
            pass
        _poller_task = None
    await close_marketplace_http_clients()
    await close_db()
    logger.info("Database connection closed")


async def main() -> None:
    settings = get_settings()
    setup_logging(settings)

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())
    dp.update.middleware(UserContextMiddleware())
    dp.include_router(main_router)

    @dp.errors()
    async def on_error(event: ErrorEvent) -> None:
        logger.exception("Unhandled bot error: {}", event.exception)
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    logger.info("Starting ReviewPilot bot")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
