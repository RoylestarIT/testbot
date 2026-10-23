from datetime import UTC, datetime
from typing import Any

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import MarketplaceAccount, Review, ReviewStatus


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
        now = datetime.now(UTC)
        stmt = stmt.where(or_(Review.snoozed_until.is_(None), Review.snoozed_until <= now))
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

    async def list_by_user(
        self,
        user_id: int,
        *,
        statuses: tuple[ReviewStatus, ...] = (ReviewStatus.PROCESSED, ReviewStatus.PUBLISHED),
        account_id: int | None = None,
        limit: int = 15,
    ) -> list[Review]:
        stmt = (
            select(Review)
            .join(MarketplaceAccount, Review.account_id == MarketplaceAccount.id)
            .where(
                MarketplaceAccount.user_id == user_id,
                Review.status.in_(statuses),
            )
        )
        if account_id is not None:
            stmt = stmt.where(Review.account_id == account_id)
        stmt = stmt.order_by(Review.created_at.desc()).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def list_new_for_user(self, user_id: int, *, limit: int = 30) -> list[Review]:
        now = datetime.now(UTC)
        stmt = (
            select(Review)
            .join(MarketplaceAccount, Review.account_id == MarketplaceAccount.id)
            .where(
                MarketplaceAccount.user_id == user_id,
                Review.status == ReviewStatus.NEW,
                or_(Review.snoozed_until.is_(None), Review.snoozed_until <= now),
            )
            .order_by(Review.created_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def snooze(self, review_id: int, until: datetime) -> Review | None:
        review = await self.get_by_id(review_id)
        if review is None:
            return None
        review.snoozed_until = until
        await self._session.flush()
        return review

    async def get_by_id_for_user(self, review_id: int, user_id: int) -> Review | None:
        result = await self._session.execute(
            select(Review)
            .join(MarketplaceAccount, Review.account_id == MarketplaceAccount.id)
            .where(Review.id == review_id, MarketplaceAccount.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def update_status(self, review_id: int, status: ReviewStatus) -> Review | None:
        review = await self.get_by_id(review_id)
        if review is None:
            return None
        review.status = status
        await self._session.flush()
        return review
