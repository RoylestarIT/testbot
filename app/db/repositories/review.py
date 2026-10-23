from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Review, ReviewStatus


class ReviewRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, review_id: int) -> Review | None:
        return await self._session.get(Review, review_id)

    async def get_by_external_id(self, account_id: int, external_id: str) -> Review | None:
        result = await self._session.execute(
            select(Review).where(
                Review.account_id == account_id,
                Review.external_id == external_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_by_account(
        self,
        account_id: int,
        *,
        status: ReviewStatus | None = None,
        limit: int = 50,
    ) -> list[Review]:
        stmt = select(Review).where(Review.account_id == account_id)
        if status is not None:
            stmt = stmt.where(Review.status == status)
        stmt = stmt.order_by(Review.created_at.desc()).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def create(
        self,
        *,
        account_id: int,
        external_id: str,
        rating: int | None = None,
        text: str | None = None,
        author: str | None = None,
        status: ReviewStatus = ReviewStatus.NEW,
        raw_json: dict[str, Any] | None = None,
    ) -> Review:
        review = Review(
            account_id=account_id,
            external_id=external_id,
            rating=rating,
            text=text,
            author=author,
            status=status,
            raw_json=raw_json,
        )
        self._session.add(review)
        await self._session.flush()
        await self._session.refresh(review)
        return review

    async def update_status(self, review_id: int, status: ReviewStatus) -> Review | None:
        review = await self.get_by_id(review_id)
        if review is None:
            return None
        review.status = status
        await self._session.flush()
        return review
