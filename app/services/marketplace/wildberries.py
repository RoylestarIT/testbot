from __future__ import annotations

from datetime import datetime
from typing import Any

import httpx
from loguru import logger

from app.core.security import decrypt_secret
from app.db.models import MarketplaceAccount
from app.services.http_client import DEFAULT_TIMEOUT, request_with_retry
from app.services.marketplace.base import MarketplaceAPIError, MarketplaceClient, MarketplaceReviewDTO

# Документация WB: https://dev.wildberries.ru/docs/openapi/user-communication
# Base URL категории «Вопросы и отзывы»
WB_FEEDBACKS_BASE_URL = "https://feedbacks-api.wildberries.ru"
WB_FEEDBACKS_LIST_PATH = "/api/v1/feedbacks"
WB_FEEDBACKS_ANSWER_PATH = "/api/v1/feedbacks/answer"
WB_QUESTIONS_LIST_PATH = "/api/v1/questions"


def _auth_headers(api_key: str) -> dict[str, str]:
    # WB API: токен в заголовке Authorization (категория Feedbacks and Questions)
    return {"Authorization": api_key}


def _parse_wb_feedback(item: dict[str, Any]) -> MarketplaceReviewDTO:
    text_parts = [item.get("text"), item.get("pros"), item.get("cons")]
    merged = "\n".join(part.strip() for part in text_parts if isinstance(part, str) and part.strip())
    created_raw = item.get("createdDate")
    created_at = None
    if isinstance(created_raw, str):
        try:
            created_at = datetime.fromisoformat(created_raw.replace("Z", "+00:00"))
        except ValueError:
            created_at = None
    return MarketplaceReviewDTO(
        external_id=str(item.get("id", "")),
        rating=int(item["productValuation"]) if item.get("productValuation") is not None else None,
        text=merged or None,
        author=str(item.get("userName")) if item.get("userName") else None,
        created_at=created_at,
        raw_json=item,
    )


class WildberriesClient(MarketplaceClient):
    def __init__(self, http_client: httpx.AsyncClient | None = None) -> None:
        self._client = http_client or httpx.AsyncClient(
            base_url=WB_FEEDBACKS_BASE_URL,
            timeout=DEFAULT_TIMEOUT,
        )
        self._owns_client = http_client is None

    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    def _token(self, account: MarketplaceAccount) -> str:
        return decrypt_secret(account.encrypted_api_key)

    async def fetch_reviews(
        self,
        account: MarketplaceAccount,
        *,
        limit: int = 20,
        unanswered_only: bool = True,
    ) -> list[MarketplaceReviewDTO]:
        target = max(1, min(limit, 5000))
        collected: list[MarketplaceReviewDTO] = []
        skip = 0
        headers = _auth_headers(self._token(account))

        while len(collected) < target:
            take = min(100, target - len(collected))
            params = {
                "isAnswered": "false" if unanswered_only else "true",
                "take": take,
                "skip": skip,
                "order": "dateDesc",
            }
            response = await request_with_retry(
                self._client,
                "GET",
                WB_FEEDBACKS_LIST_PATH,
                headers=headers,
                params=params,
            )
            if response.status_code == 401:
                raise MarketplaceAPIError("WB: не авторизован (проверьте API-ключ)", status_code=401)
            if response.status_code >= 400:
                raise MarketplaceAPIError(
                    f"WB: ошибка получения отзывов ({response.status_code})",
                    status_code=response.status_code,
                )
            payload = response.json()
            data = payload.get("data") if isinstance(payload, dict) else None
            items = data.get("feedbacks", []) if isinstance(data, dict) else []
            if not isinstance(items, list) or not items:
                break
            for item in items:
                if isinstance(item, dict):
                    collected.append(_parse_wb_feedback(item))
            skip += len(items)
            if len(items) < take:
                break

        return collected[:target]

    async def publish_reply(
        self,
        account: MarketplaceAccount,
        review_external_id: str,
        text: str,
    ) -> None:
        body = {"id": review_external_id, "text": text}
        response = await request_with_retry(
            self._client,
            "POST",
            WB_FEEDBACKS_ANSWER_PATH,
            headers={
                **_auth_headers(self._token(account)),
                "Content-Type": "application/json",
            },
            json=body,
        )
        if response.status_code == 204:
            logger.info("WB reply published for review_id={}", review_external_id)
            return
        if response.status_code == 401:
            raise MarketplaceAPIError("WB: не авторизован при публикации", status_code=401)
        raise MarketplaceAPIError(
            f"WB: не удалось опубликовать ответ ({response.status_code})",
            status_code=response.status_code,
        )

    async def test_connection(self, account: MarketplaceAccount) -> MarketplaceReviewDTO | None:
        reviews = await self.fetch_reviews(account, limit=1, unanswered_only=False)
        return reviews[0] if reviews else None

    async def count_unanswered_questions(self, account: MarketplaceAccount, *, cap: int = 500) -> int:
        """Число неотвеченных вопросов покупателей (WB Questions API)."""
        headers = _auth_headers(self._token(account))
        total = 0
        skip = 0
        while total < cap:
            take = min(100, cap - total)
            params = {
                "isAnswered": "false",
                "take": take,
                "skip": skip,
                "order": "dateDesc",
            }
            response = await request_with_retry(
                self._client,
                "GET",
                WB_QUESTIONS_LIST_PATH,
                headers=headers,
                params=params,
            )
            if response.status_code == 401:
                raise MarketplaceAPIError("WB: не авторизован (вопросы)", status_code=401)
            if response.status_code >= 400:
                raise MarketplaceAPIError(
                    f"WB: ошибка получения вопросов ({response.status_code})",
                    status_code=response.status_code,
                )
            payload = response.json()
            data = payload.get("data") if isinstance(payload, dict) else None
            items = data.get("questions", []) if isinstance(data, dict) else []
            if not isinstance(items, list) or not items:
                break
            total += len(items)
            skip += len(items)
            if len(items) < take:
                break
        return total

    async def list_unanswered_questions(
        self,
        account: MarketplaceAccount,
        *,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        headers = _auth_headers(self._token(account))
        params = {
            "isAnswered": "false",
            "take": min(limit, 20),
            "skip": 0,
            "order": "dateDesc",
        }
        response = await request_with_retry(
            self._client,
            "GET",
            WB_QUESTIONS_LIST_PATH,
            headers=headers,
            params=params,
        )
        if response.status_code == 401:
            raise MarketplaceAPIError("WB: не авторизован (вопросы)", status_code=401)
        if response.status_code >= 400:
            raise MarketplaceAPIError(
                f"WB: ошибка получения вопросов ({response.status_code})",
                status_code=response.status_code,
            )
        payload = response.json()
        data = payload.get("data") if isinstance(payload, dict) else None
        items = data.get("questions", []) if isinstance(data, dict) else []
        if not isinstance(items, list):
            return []
        return [item for item in items if isinstance(item, dict)][:limit]
