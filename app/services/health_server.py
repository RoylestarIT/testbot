from __future__ import annotations

from aiohttp import web
from loguru import logger


async def _health_handler(_request: web.Request) -> web.Response:
    db_ok = True
    try:
        from sqlalchemy import text

        from app.db.session import get_session_factory

        session_factory = get_session_factory()
        async with session_factory() as session:
            await session.execute(text("SELECT 1"))
    except Exception:
        db_ok = False
        logger.exception("Health check: database unavailable")

    from app.tasks.poller import get_poller_health

    from app.services.bot_activity import activity_snapshot

    payload: dict[str, object] = {
        "status": "ok" if db_ok else "degraded",
        "service": "reviewpilot",
        "db": db_ok,
        "poller": get_poller_health(),
        "bot": activity_snapshot(),
    }
    status = 200 if db_ok else 503
    return web.json_response(payload, status=status)


async def start_health_server(host: str, port: int, *, bot: object | None = None) -> web.AppRunner:
    app = web.Application()
    app.router.add_get("/health", _health_handler)
    if bot is not None:
        from app.services.payment.crypto_webhook import register_crypto_webhook_routes

        register_crypto_webhook_routes(app, bot=bot)  # type: ignore[arg-type]
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    await site.start()
    logger.info("Health server listening on {}:{}", host, port)
    return runner
