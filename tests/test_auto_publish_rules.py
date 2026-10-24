import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.models import Base, Marketplace, MarketplaceAccount, Review, ReviewStatus, User
from app.services.marketplace.auto_publish import try_auto_publish_review


@pytest.fixture
async def session() -> AsyncSession:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        yield session
    await engine.dispose()


@pytest.mark.asyncio
async def test_auto_publish_skips_rating_below_min(session: AsyncSession) -> None:
    user = User(tg_id=1, username="u")
    session.add(user)
    await session.flush()
    acc = MarketplaceAccount(
        user_id=user.id,
        marketplace=Marketplace.WB,
        encrypted_api_key="x",
        auto_publish_enabled=True,
        auto_publish_min_rating=5,
    )
    session.add(acc)
    await session.flush()
    review = Review(
        account_id=acc.id,
        external_id="r1",
        rating=4,
        text="ok",
        status=ReviewStatus.NEW,
    )
    session.add(review)
    await session.flush()
    outcome = await try_auto_publish_review(session, account=acc, review=review)
    assert outcome.status == "skipped"


@pytest.mark.asyncio
async def test_auto_publish_skips_when_stars_only_and_text(session: AsyncSession) -> None:
    user = User(tg_id=2, username="v")
    session.add(user)
    await session.flush()
    acc = MarketplaceAccount(
        user_id=user.id,
        marketplace=Marketplace.WB,
        encrypted_api_key="x",
        auto_publish_enabled=True,
        auto_publish_min_rating=5,
        auto_publish_stars_only=True,
    )
    session.add(acc)
    await session.flush()
    review = Review(
        account_id=acc.id,
        external_id="r2",
        rating=5,
        text="есть текст",
        status=ReviewStatus.NEW,
    )
    session.add(review)
    await session.flush()
    outcome = await try_auto_publish_review(session, account=acc, review=review)
    assert outcome.status == "skipped"


@pytest.mark.asyncio
async def test_auto_publish_skips_stop_words(session: AsyncSession) -> None:
    user = User(tg_id=3, username="w")
    session.add(user)
    await session.flush()
    acc = MarketplaceAccount(
        user_id=user.id,
        marketplace=Marketplace.WB,
        encrypted_api_key="x",
        auto_publish_enabled=True,
        auto_publish_min_rating=5,
        auto_publish_stop_words="брак, возврат",
    )
    session.add(acc)
    await session.flush()
    review = Review(
        account_id=acc.id,
        external_id="r3",
        rating=5,
        text="Пришёл с браком",
        status=ReviewStatus.NEW,
    )
    session.add(review)
    await session.flush()
    outcome = await try_auto_publish_review(session, account=acc, review=review)
    assert outcome.status == "skipped"
