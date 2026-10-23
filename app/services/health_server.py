from __future__ import annotations

from aiohttp import web
from loguru import logger


async def _health_handler(_request: web.Request) -> web.Response:
    return web.json_response({"status": "ok", "service": "reviewpilot"})


async def start_health_server(host: str, port: int) -> web.AppRunner:
    app = web.Application()
    app.router.add_get("/health", _health_handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    await site.start()
    logger.info("Health server listening on {}:{}", host, port)
    return runner
