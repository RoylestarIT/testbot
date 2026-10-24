from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from app.db.models import MarketplaceAccount


@dataclass(slots=True)
class MarketplaceReviewDTO:
    external_id: str
    rating: int | None
    text: str | None
    author: str | None
    created_at: datetime | None
    raw_json: dict[str, Any]


class MarketplaceAPIError(Exception):
    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class MarketplaceClient(ABC):
    @abstractmethod
    async def fetch_reviews(
        self,
        account: MarketplaceAccount,
        *,
        limit: int = 20,
        unanswered_only: bool = True,
    ) -> list[MarketplaceReviewDTO]:
        raise NotImplementedError

    @abstractmethod
    async def publish_reply(
        self,
        account: MarketplaceAccount,
        review_external_id: str,
        text: str,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def test_connection(self, account: MarketplaceAccount) -> MarketplaceReviewDTO | None:
        """Пробный запрос (например, 1 отзыв). None — если отзывов нет, но ключ валиден."""
        raise NotImplementedError
