import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.constants import MANUAL_SHOP_NAME
from app.db.models import Base, Marketplace, MarketplaceAccount, Review, ReviewStatus
from app.services.marketplace.base import MarketplaceAPIError
from app.services.marketplace.publish_service import publish_reply_to_marketplace


@pytest.fixture
async def session() -> AsyncSession:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        yield session
    await engine.dispose()


async def _review(session: AsyncSession, *, shop_name: str | None, api_key: str) -> Review:
    account = MarketplaceAccount(
        user_id=1,
        marketplace=Marketplace.WB,
        encrypted_api_key=api_key,
        shop_name=shop_name,
        is_active=True,
    )
    session.add(account)
    await session.flush()
    review = Review(account_id=account.id, external_id="e1", status=ReviewStatus.NEW, rating=5)
    session.add(review)
    await session.flush()
    return review


async def test_manual_account_publish_is_rejected_with_friendly_error(session: AsyncSession) -> None:
    review = await _review(session, shop_name=MANUAL_SHOP_NAME, api_key="not-a-fernet-token")
    with pytest.raises(MarketplaceAPIError, match="скопируйте ответ"):
        await publish_reply_to_marketplace(session, review, "Спасибо!")


async def test_undecryptable_key_becomes_marketplace_error(session: AsyncSession) -> None:
    review = await _review(session, shop_name="Мой магазин", api_key="not-a-fernet-token")
    with pytest.raises(MarketplaceAPIError, match="подключите кабинет заново"):
        await publish_reply_to_marketplace(session, review, "Спасибо!")
