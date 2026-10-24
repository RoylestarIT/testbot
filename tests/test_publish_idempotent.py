import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.models import Base, Marketplace, MarketplaceAccount, Review, ReviewStatus
from app.services.marketplace.base import MarketplaceAPIError
from app.services.marketplace.publish_service import publish_reply_to_marketplace


@pytest.mark.asyncio
async def test_publish_skips_already_published() -> None:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as session:
        account = MarketplaceAccount(
            user_id=1,
            marketplace=Marketplace.WB,
            encrypted_api_key="x",
            is_active=True,
        )
        session.add(account)
        await session.flush()
        review = Review(
            account_id=account.id,
            external_id="e1",
            status=ReviewStatus.PUBLISHED,
            rating=5,
            text="ok",
        )
        session.add(review)
        await session.flush()

        with pytest.raises(MarketplaceAPIError, match="уже опубликован"):
            await publish_reply_to_marketplace(session, review, "text")

    await engine.dispose()
