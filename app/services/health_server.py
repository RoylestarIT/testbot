from __future__ import annotations

from aiohttp import web
from loguru import logger


def _cors_headers(request: web.Request, allowed_origins: str) -> dict[str, str]:
    origin = request.headers.get("Origin", "")
    allowed = [o.strip() for o in allowed_origins.split(",") if o.strip()]
    if not allowed or (origin and origin in allowed):
        return {
            "Access-Control-Allow-Origin": origin if origin in allowed else allowed[0],
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Cache-Control": "public, max-age=300",
        }
    return {}


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


async def _public_metrics_handler(request: web.Request) -> web.Response:
    from app.core.config import get_settings

    settings = get_settings()
    headers = _cors_headers(request, settings.public_metrics_cors_origins)

    if request.method == "OPTIONS":
        return web.Response(status=204, headers=headers)

    try:
        from app.db.session import get_session_factory
        from app.services.public_metrics import build_public_metrics

        session_factory = get_session_factory()
        async with session_factory() as session:
            payload = await build_public_metrics(session)
    except Exception:
        logger.exception("Public metrics unavailable")
        return web.json_response({"error": "unavailable"}, status=503, headers=headers)

    return web.json_response(payload, headers=headers)


async def start_health_server(host: str, port: int, *, bot: object | None = None) -> web.AppRunner:
    from app.core.config import get_settings

    app = web.Application()
    app.router.add_get("/health", _health_handler)
    settings = get_settings()
    if settings.public_metrics_enabled:
        app.router.add_route("GET", "/public/metrics", _public_metrics_handler)
        app.router.add_route("OPTIONS", "/public/metrics", _public_metrics_handler)
        logger.info("Public metrics enabled at GET /public/metrics")
    if bot is not None:
        from app.services.payment.crypto_webhook import register_crypto_webhook_routes

        register_crypto_webhook_routes(app, bot=bot)  # type: ignore[arg-type]
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    await site.start()
    logger.info("Health server listening on {}:{}", host, port)
    return runner
