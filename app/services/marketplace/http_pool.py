from __future__ import annotations

import httpx

from app.services.http_client import DEFAULT_TIMEOUT
from app.services.marketplace.ozon import OZON_SELLER_BASE_URL
from app.services.marketplace.wildberries import WB_FEEDBACKS_BASE_URL

_wb_client: httpx.AsyncClient | None = None
_ozon_client: httpx.AsyncClient | None = None


def get_wb_http_client() -> httpx.AsyncClient:
    global _wb_client
    if _wb_client is None:
        _wb_client = httpx.AsyncClient(base_url=WB_FEEDBACKS_BASE_URL, timeout=DEFAULT_TIMEOUT)
    return _wb_client


def get_ozon_http_client() -> httpx.AsyncClient:
    global _ozon_client
    if _ozon_client is None:
        _ozon_client = httpx.AsyncClient(base_url=OZON_SELLER_BASE_URL, timeout=DEFAULT_TIMEOUT)
    return _ozon_client


async def close_marketplace_http_clients() -> None:
    global _wb_client, _ozon_client
    if _wb_client is not None:
        await _wb_client.aclose()
        _wb_client = None
    if _ozon_client is not None:
        await _ozon_client.aclose()
        _ozon_client = None
