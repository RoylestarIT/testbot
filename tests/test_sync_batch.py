import pytest
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

from app.db.models import Marketplace, ReviewStatus
from app.services.marketplace.base import MarketplaceReviewDTO
from app.services.marketplace.sync_service import sync_account_reviews


@pytest.mark.asyncio
async def test_sync_skips_existing_external_ids_in_batch() -> None:
    account = MagicMock()
    account.id = 1
    account.user_id = 1
    account.marketplace = Marketplace.WB
    account.last_sync_at = None
    account.last_sync_error = None

    client = AsyncMock()
    client.fetch_reviews = AsyncMock(
        return_value=[
            MarketplaceReviewDTO(
                external_id="a1",
                rating=5,
                text="Ok",
                author=None,
                created_at=datetime.now(UTC),
                raw_json={},
            ),
            MarketplaceReviewDTO(
                external_id="a2",
                rating=4,
                text="Hi",
                author=None,
                created_at=datetime.now(UTC),
                raw_json={},
            ),
        ]
    )

    session = MagicMock()
    session.flush = AsyncMock()
    repo = MagicMock()
    repo.existing_external_ids = AsyncMock(return_value={"a1"})
    created_reviews = []

    async def _create(**kwargs):
        review = MagicMock()
        review.id = len(created_reviews) + 1
        review.status = ReviewStatus.NEW
        for k, v in kwargs.items():
            setattr(review, k, v)
        created_reviews.append(review)
        return review

    repo.create = AsyncMock(side_effect=_create)
    repo.get_by_external_id = AsyncMock()

    import app.services.marketplace.sync_service as sync_mod

    original_repo = sync_mod.ReviewRepository
    sync_mod.ReviewRepository = lambda _s: repo  # type: ignore[misc, assignment]
    try:
        created, fetched, reviews = await sync_account_reviews(session, account, client=client)
    finally:
        sync_mod.ReviewRepository = original_repo

    assert fetched == 2
    assert created == 1
    assert len(reviews) == 1
    assert reviews[0].external_id == "a2"
    repo.create.assert_awaited_once()
