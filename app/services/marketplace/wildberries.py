from __future__ import annotations

import base64
import json
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
WB_FEEDBACKS_SANDBOX_BASE_URL = "https://feedbacks-api-sandbox.wildberries.ru"
WB_FEEDBACKS_LIST_PATH = "/api/v1/feedbacks"
WB_FEEDBACKS_ANSWER_PATH = "/api/v1/feedbacks/answer"
WB_QUESTIONS_LIST_PATH = "/api/v1/questions"


def decode_wb_jwt_payload(token: str) -> dict[str, Any]:
    """Decode JWT payload without signature verification (WB token introspection)."""
    parts = token.split(".")
    if len(parts) != 3:
        return {}
    pad = "=" * (-len(parts[1]) % 4)
    try:
        raw = base64.urlsafe_b64decode(parts[1] + pad)
        data = json.loads(raw)
        return data if isinstance(data, dict) else {}
    except (ValueError, json.JSONDecodeError):
        return {}


def wb_token_is_test(token: str) -> bool:
    payload = decode_wb_jwt_payload(token)
    if payload.get("t") is True:
        return True
    # acc=2 → test token per WB API docs
    return payload.get("acc") == 2


def wb_feedbacks_api_root(token: str) -> str:
    if wb_token_is_test(token):
        return WB_FEEDBACKS_SANDBOX_BASE_URL
    return WB_FEEDBACKS_BASE_URL


def normalize_wb_api_key(raw: str) -> str:
    """Trim Telegram paste artifacts; WB expects raw JWT in Authorization."""
    key = (raw or "").strip().strip('"').strip("'")
    if key.startswith("```"):
        lines = [ln for ln in key.splitlines() if not ln.strip().startswith("```")]
        key = "\n".join(lines).strip()
    if key.lower().startswith("bearer "):
        key = key[7:].strip()
    return key


def _auth_headers(api_key: str) -> dict[str, str]:
    # WB API: токен в заголовке Authorization (категория Feedbacks and Questions)
    return {"Authorization": api_key}


def _wb_error_message(response: httpx.Response, *, context: str) -> str:
    detail = ""
    try:
        body = response.json()
        if isinstance(body, dict):
            detail = str(body.get("detail") or body.get("title") or "").strip()
    except Exception:
        detail = (response.text or "")[:200].strip()
    code = response.status_code
    if code == 401:
        hint = "Проверьте, что ключ скопирован целиком и из категории «Вопросы и отзывы»."
        if detail:
            return f"WB: не авторизован — {detail}. {hint}"
        return f"WB: не авторизован (проверьте API-ключ). {hint}"
    if code == 403:
        return (
            "WB: доступ запрещён (403). Частые причины: токен «для разработки/тестовый» отправлен на боевой API "
            "(нужен sandbox — бот переключается сам), либо ключ не из категории «Вопросы и отзывы», "
            "либо только чтение без прав на отзывы. Для реального магазина создайте персональный токен "
            "в seller.wildberries.ru → Настройки → Доступ к API."
        )
    if code == 429:
        return "WB: слишком много запросов (429). Подождите минуту и попробуйте снова."
    if detail:
        return f"WB: {context} ({code}) — {detail}"
    return f"WB: {context} ({code})"


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
        # No fixed base_url: prod vs sandbox depends on token type (test JWT → sandbox).
        self._client = http_client or httpx.AsyncClient(timeout=DEFAULT_TIMEOUT)
        self._owns_client = http_client is None

    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    def _token(self, account: MarketplaceAccount) -> str:
        token = normalize_wb_api_key(decrypt_secret(account.encrypted_api_key))
        if token.count(".") != 2:
            raise MarketplaceAPIError(
                "WB: ключ не похож на API-токен. Скопируйте JWT целиком из кабинета "
                "(категория «Вопросы и отзывы»), без пробелов и переносов строк."
            )
        return token

    def _api_url(self, account: MarketplaceAccount, path: str) -> str:
        root = wb_feedbacks_api_root(self._token(account)).rstrip("/")
        return f"{root}{path}"

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
        token = self._token(account)
        headers = _auth_headers(token)
        list_url = self._api_url(account, WB_FEEDBACKS_LIST_PATH)

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
                list_url,
                headers=headers,
                params=params,
            )
            if response.status_code >= 400:
                raise MarketplaceAPIError(
                    _wb_error_message(response, context="ошибка получения отзывов"),
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
            self._api_url(account, WB_FEEDBACKS_ANSWER_PATH),
            headers={
                **_auth_headers(self._token(account)),
                "Content-Type": "application/json",
            },
            json=body,
        )
        if response.status_code == 204:
            logger.info("WB reply published for review_id={}", review_external_id)
            return
        if response.status_code >= 400:
            raise MarketplaceAPIError(
                _wb_error_message(response, context="не удалось опубликовать ответ"),
                status_code=response.status_code,
            )

    async def test_connection(self, account: MarketplaceAccount) -> MarketplaceReviewDTO | None:
        reviews = await self.fetch_reviews(account, limit=1, unanswered_only=False)
        return reviews[0] if reviews else None

    async def count_unanswered_questions(self, account: MarketplaceAccount, *, cap: int = 500) -> int:
        """Число неотвеченных вопросов покупателей (WB Questions API)."""
        headers = _auth_headers(self._token(account))
        questions_url = self._api_url(account, WB_QUESTIONS_LIST_PATH)
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
                questions_url,
                headers=headers,
                params=params,
            )
            if response.status_code >= 400:
                raise MarketplaceAPIError(
                    _wb_error_message(response, context="ошибка получения вопросов"),
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
            self._api_url(account, WB_QUESTIONS_LIST_PATH),
            headers=headers,
            params=params,
        )
        if response.status_code >= 400:
            raise MarketplaceAPIError(
                _wb_error_message(response, context="ошибка получения вопросов"),
                status_code=response.status_code,
            )
        payload = response.json()
        data = payload.get("data") if isinstance(payload, dict) else None
        items = data.get("questions", []) if isinstance(data, dict) else []
        if not isinstance(items, list):
            return []
        return [item for item in items if isinstance(item, dict)][:limit]
