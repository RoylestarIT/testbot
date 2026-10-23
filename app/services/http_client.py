from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import Any

import httpx
from loguru import logger

DEFAULT_TIMEOUT = httpx.Timeout(connect=10.0, read=30.0, write=10.0, pool=10.0)
DEFAULT_RETRIES = 3
DEFAULT_BACKOFF_SEC = 0.5


async def request_with_retry(
    client: httpx.AsyncClient,
    method: str,
    url: str,
    *,
    retries: int = DEFAULT_RETRIES,
    backoff_sec: float = DEFAULT_BACKOFF_SEC,
    retry_on_status: frozenset[int] = frozenset({429, 500, 502, 503, 504}),
    **kwargs: Any,
) -> httpx.Response:
    last_exc: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            response = await client.request(method, url, **kwargs)
            if response.status_code in retry_on_status and attempt < retries:
                logger.warning(
                    "HTTP {} {} attempt {}/{}",
                    response.status_code,
                    url,
                    attempt,
                    retries,
                )
                await asyncio.sleep(backoff_sec * attempt)
                continue
            return response
        except (httpx.TimeoutException, httpx.TransportError) as exc:
            last_exc = exc
            logger.warning("HTTP transport error {} attempt {}/{}", url, attempt, retries)
            if attempt >= retries:
                raise
            await asyncio.sleep(backoff_sec * attempt)
    if last_exc:
        raise last_exc
    raise RuntimeError("request_with_retry failed without response")


async def run_sync[T](func: Callable[[], T]) -> T:
    return await asyncio.to_thread(func)
