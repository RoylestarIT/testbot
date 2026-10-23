from __future__ import annotations

from aiohttp import web
from loguru import logger


async def _health_handler(_request: web.Request) -> web.Response:
    db_ok = True
    db_error: str | None = None
    try:
        from sqlalchemy import text

        from app.db.session import get_session_factory

        session_factory = get_session_factory()
        async with session_factory() as session:
            await session.execute(text("SELECT 1"))
    except Exception as exc:
        db_ok = False
        db_error = str(exc)[:200]

    payload: dict[str, object] = {"status": "ok" if db_ok else "degraded", "service": "reviewpilot", "db": db_ok}
    if db_error:
        payload["db_error"] = db_error
    status = 200 if db_ok else 503
    return web.json_response(payload, status=status)


async def start_health_server(host: str, port: int) -> web.AppRunner:
    app = web.Application()
    app.router.add_get("/health", _health_handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    await site.start()
    logger.info("Health server listening on {}:{}", host, port)
    return runner
