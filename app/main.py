import asyncio

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import ErrorEvent
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import CallbackQuery, Message
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
from app.tasks.poller_health_alert import poller_health_alert_loop

_poller_task: asyncio.Task[None] | None = None
_reminder_task: asyncio.Task[None] | None = None
_digest_task: asyncio.Task[None] | None = None
_stale_reminder_task: asyncio.Task[None] | None = None
_crypto_poller_task: asyncio.Task[None] | None = None
_poller_health_task: asyncio.Task[None] | None = None
_health_runner: web.AppRunner | None = None


async def on_startup(bot: Bot) -> None:
    global _poller_task, _reminder_task, _digest_task, _stale_reminder_task, _crypto_poller_task, _poller_health_task, _health_runner
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
    from app.bot.bot_profile import apply_bot_profile

    await apply_bot_profile(bot, settings)
    _poller_task = asyncio.create_task(marketplace_poller_loop(bot))
    _reminder_task = asyncio.create_task(subscription_reminder_loop(bot))
    _digest_task = asyncio.create_task(daily_digest_loop(bot))
    _stale_reminder_task = asyncio.create_task(stale_review_reminder_loop(bot))
    _crypto_poller_task = asyncio.create_task(crypto_pay_poller_loop(bot))
    _poller_health_task = asyncio.create_task(poller_health_alert_loop(bot))
    if settings.health_port > 0:
        _health_runner = await start_health_server(settings.webhook_host, settings.health_port, bot=bot)


async def on_shutdown(*_args: object, **_kwargs: object) -> None:
    global _poller_task, _reminder_task, _digest_task, _stale_reminder_task, _crypto_poller_task, _poller_health_task, _health_runner
    await stop_llm_workers()
    for task in (
        _poller_task,
        _reminder_task,
        _digest_task,
        _stale_reminder_task,
        _crypto_poller_task,
        _poller_health_task,
    ):
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
    _poller_health_task = None
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
    storage = MemoryStorage()
    if settings.fsm_redis_url.strip():
        from aiogram.fsm.storage.redis import RedisStorage

        storage = RedisStorage.from_url(settings.fsm_redis_url.strip())
        logger.info("FSM storage: Redis")
    else:
        logger.info("FSM storage: memory")

    dp = Dispatcher(storage=storage)
    dp.update.middleware(UserContextMiddleware())
    dp.include_router(main_router)

    @dp.errors()
    async def on_error(event: ErrorEvent) -> None:
        logger.exception("Unhandled bot error: {}", event.exception)
        update = event.update
        hint = "⚠️ Что-то пошло не так. Попробуйте /start или повторите действие."
        try:
            if update.callback_query is not None:
                cq: CallbackQuery = update.callback_query
                await cq.answer("Ошибка. Попробуйте снова.", show_alert=True)
                if cq.message is not None:
                    await cq.message.answer(hint)
            elif update.message is not None:
                msg: Message = update.message
                await msg.answer(hint)
        except Exception:
            logger.warning("Failed to send user-facing error hint")

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
