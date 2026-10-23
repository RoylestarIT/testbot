import asyncio

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand, ErrorEvent
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from loguru import logger

from app.bot.handlers import main_router
from app.bot.middlewares.user_context import UserContextMiddleware
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.db.session import close_db, init_db
from app.services.health_server import start_health_server
from app.services.marketplace.http_pool import close_marketplace_http_clients
from app.services.llm_queue import start_llm_workers, stop_llm_workers
from app.tasks.crypto_pay_poller import crypto_pay_poller_loop
from app.tasks.daily_digest import daily_digest_loop
from app.tasks.stale_review_reminder import stale_review_reminder_loop
from app.tasks.poller import marketplace_poller_loop
from app.tasks.subscription_reminder import subscription_reminder_loop

_poller_task: asyncio.Task[None] | None = None
_reminder_task: asyncio.Task[None] | None = None
_digest_task: asyncio.Task[None] | None = None
_stale_reminder_task: asyncio.Task[None] | None = None
_crypto_poller_task: asyncio.Task[None] | None = None
_health_runner: web.AppRunner | None = None


async def _register_bot_commands(bot: Bot) -> None:
    await bot.set_my_commands(
        [
            BotCommand(command="start", description="🏠 Сводка · co-pilot WB/Ozon"),
            BotCommand(command="dashboard", description="📊 Сводка и статусы"),
            BotCommand(command="help", description="📖 Справка по боту"),
            BotCommand(command="my_subscription", description="💎 Моя подписка"),
            BotCommand(command="promo", description="🎟 Активировать промокод"),
            BotCommand(command="admin", description="🛠 Админ-панель"),
        ]
    )


async def on_startup(bot: Bot) -> None:
    global _poller_task, _reminder_task, _digest_task, _stale_reminder_task, _crypto_poller_task, _health_runner
    settings = get_settings()
    await init_db()
    logger.info("Database initialized")
    start_llm_workers(concurrency=settings.llm_queue_workers)
    if settings.crypto_pay_api_token.strip():
        try:
            from app.services.payment.crypto_pay import _api_request

            me = await _api_request(settings, "getMe")
            name = me.get("name") if isinstance(me, dict) else me
            logger.info("Crypto Pay connected app={}", name)
        except Exception as exc:
            logger.warning("Crypto Pay getMe failed: {}", exc)
    await _register_bot_commands(bot)
    _poller_task = asyncio.create_task(marketplace_poller_loop(bot))
    _reminder_task = asyncio.create_task(subscription_reminder_loop(bot))
    _digest_task = asyncio.create_task(daily_digest_loop(bot))
    _stale_reminder_task = asyncio.create_task(stale_review_reminder_loop(bot))
    _crypto_poller_task = asyncio.create_task(crypto_pay_poller_loop(bot))
    if settings.health_port > 0:
        _health_runner = await start_health_server(settings.webhook_host, settings.health_port, bot=bot)


async def on_shutdown(*_args: object, **_kwargs: object) -> None:
    global _poller_task, _reminder_task, _digest_task, _stale_reminder_task, _crypto_poller_task, _health_runner
    await stop_llm_workers()
    for task in (_poller_task, _reminder_task, _digest_task, _stale_reminder_task, _crypto_poller_task):
        if task is not None:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
    _poller_task = None
    _reminder_task = None
    _digest_task = None
    _stale_reminder_task = None
    _crypto_poller_task = None
    if _health_runner is not None:
        await _health_runner.cleanup()
        _health_runner = None
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

    webhook_url = settings.webhook_url.strip()
    if webhook_url:
        logger.info("Starting ReviewPilot bot (webhook mode)")
        await on_startup(bot)
        app = web.Application()
        webhook_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
        webhook_handler.register(app, path=settings.webhook_path)
        setup_application(app, dp, bot=bot)
        from app.services.payment.crypto_webhook import register_crypto_webhook_routes

        register_crypto_webhook_routes(app, bot=bot, settings=settings)

        async def _cleanup_webhook(_app: web.Application) -> None:
            await on_shutdown()

        app.on_cleanup.append(_cleanup_webhook)
        await bot.set_webhook(webhook_url)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, settings.webhook_host, settings.webhook_port)
        await site.start()
        logger.info("Webhook listening on {}:{}{}", settings.webhook_host, settings.webhook_port, settings.webhook_path)
        try:
            await asyncio.Event().wait()
        finally:
            await on_shutdown()
    else:
        logger.info("Starting ReviewPilot bot (polling)")
        await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
