from __future__ import annotations

from datetime import datetime
from typing import Any

import httpx
from loguru import logger

from app.core.security import decrypt_secret
from app.db.models import MarketplaceAccount
from app.services.http_client import DEFAULT_TIMEOUT, request_with_retry
from app.services.marketplace.base import MarketplaceAPIError, MarketplaceClient, MarketplaceReviewDTO

# Документация Ozon Seller API (ReviewAPI):
# POST https://api-seller.ozon.ru/v1/review/list
OZON_SELLER_BASE_URL = "https://api-seller.ozon.ru"
OZON_REVIEW_LIST_PATH = "/v1/review/list"
OZON_REVIEW_COMMENT_CREATE_PATH = "/v1/review/comment/create"


def _ozon_headers(client_id: str, api_key: str) -> dict[str, str]:
    return {
        "Client-Id": client_id,
        "Api-Key": api_key,
        "Content-Type": "application/json",
    }


def _parse_ozon_review(item: dict[str, Any]) -> MarketplaceReviewDTO:
    published_raw = item.get("published_at")
    created_at = None
    if isinstance(published_raw, str):
        try:
            created_at = datetime.fromisoformat(published_raw.replace("Z", "+00:00"))
        except ValueError:
            created_at = None
    rating_raw = item.get("rating")
    return MarketplaceReviewDTO(
        external_id=str(item.get("id", "")),
        rating=int(rating_raw) if rating_raw is not None else None,
        text=str(item.get("text")) if item.get("text") else None,
        author=None,
        created_at=created_at,
        raw_json=item,
    )


class OzonClient(MarketplaceClient):
    def __init__(self, http_client: httpx.AsyncClient | None = None) -> None:
        self._client = http_client or httpx.AsyncClient(
            base_url=OZON_SELLER_BASE_URL,
            timeout=DEFAULT_TIMEOUT,
        )
        self._owns_client = http_client is None

    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    def _credentials(self, account: MarketplaceAccount) -> tuple[str, str]:
        if not account.encrypted_client_id:
            raise MarketplaceAPIError("Ozon: не указан Client-Id")
        client_id = decrypt_secret(account.encrypted_client_id)
        api_key = decrypt_secret(account.encrypted_api_key)
        return client_id, api_key

    async def fetch_reviews(
        self,
        account: MarketplaceAccount,
        *,
        limit: int = 20,
        unanswered_only: bool = True,
    ) -> list[MarketplaceReviewDTO]:
        client_id, api_key = self._credentials(account)
        remaining = max(1, limit)
        last_id: str | None = None
        collected: list[MarketplaceReviewDTO] = []

        while remaining > 0:
            page_limit = max(20, min(remaining, 100))
            body: dict[str, Any] = {
                "limit": page_limit,
                "sort_dir": "DESC",
            }
            if unanswered_only:
                body["status"] = "UNPROCESSED"
            else:
                body["status"] = "ALL"
            if last_id:
                body["last_id"] = last_id

            response = await request_with_retry(
                self._client,
                "POST",
                OZON_REVIEW_LIST_PATH,
                headers=_ozon_headers(client_id, api_key),
                json=body,
            )
            if response.status_code == 401:
                raise MarketplaceAPIError("Ozon: не авторизован", status_code=401)
            if response.status_code == 403:
                raise MarketplaceAPIError(
                    "Ozon: доступ запрещён (нужна подписка Premium Plus / Управление отзывами?)",
                    status_code=403,
                )
            if response.status_code >= 400:
                raise MarketplaceAPIError(
                    f"Ozon: ошибка получения отзывов ({response.status_code})",
                    status_code=response.status_code,
                )

            payload = response.json()
            if not isinstance(payload, dict):
                break
            items = payload.get("reviews", [])
            if not isinstance(items, list):
                break
            for item in items:
                if isinstance(item, dict):
                    collected.append(_parse_ozon_review(item))
            remaining = limit - len(collected)
            if remaining <= 0 or not payload.get("has_next"):
                break
            next_last = payload.get("last_id")
            if not next_last or not items:
                break
            last_id = str(next_last)

        return collected[:limit]

    async def publish_reply(
        self,
        account: MarketplaceAccount,
        review_external_id: str,
        text: str,
    ) -> None:
        client_id, api_key = self._credentials(account)
        body = {
            "review_id": review_external_id,
            "text": text,
            "mark_review_as_processed": True,
        }
        response = await request_with_retry(
            self._client,
            "POST",
            OZON_REVIEW_COMMENT_CREATE_PATH,
            headers=_ozon_headers(client_id, api_key),
            json=body,
        )
        if response.status_code == 200:
            logger.info("Ozon reply published for review_id={}", review_external_id)
            return
        if response.status_code == 401:
            raise MarketplaceAPIError("Ozon: не авторизован при публикации", status_code=401)
        raise MarketplaceAPIError(
            f"Ozon: не удалось опубликовать ответ ({response.status_code})",
            status_code=response.status_code,
        )

    async def test_connection(self, account: MarketplaceAccount) -> MarketplaceReviewDTO | None:
        reviews = await self.fetch_reviews(account, limit=20, unanswered_only=False)
        return reviews[0] if reviews else None
