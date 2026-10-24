import pytest
from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.db.models import Base, Marketplace, MarketplaceAccount, Review, ReviewStatus, User
from app.db.repositories.review import ReviewRepository


@pytest.fixture
async def review_order_session(tmp_path, monkeypatch: pytest.MonkeyPatch):
    db_path = tmp_path / "order.db"
    url = f"sqlite+aiosqlite:///{db_path}"
    monkeypatch.setenv("DATABASE_URL", url)
    get_settings.cache_clear()
    engine = create_async_engine(url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        user = User(tg_id=1, username="u")
        session.add(user)
        await session.flush()
        acc = MarketplaceAccount(
            user_id=user.id,
            marketplace=Marketplace.WB,
            encrypted_api_key="x",
            is_active=True,
        )
        session.add(acc)
        await session.flush()
        now = datetime.now(UTC)
        session.add_all(
            [
                Review(
                    account_id=acc.id,
                    external_id="5star",
                    rating=5,
                    text="new",
                    status=ReviewStatus.NEW,
                    created_at=now,
                ),
                Review(
                    account_id=acc.id,
                    external_id="bad",
                    rating=2,
                    text="old bad",
                    status=ReviewStatus.NEW,
                    created_at=now - timedelta(days=2),
                ),
            ]
        )
        await session.commit()
        yield factory, user.id
    await engine.dispose()
    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_list_new_prioritizes_low_ratings(review_order_session) -> None:
    factory, user_id = review_order_session
    async with factory() as session:
        reviews = await ReviewRepository(session).list_new_for_user(user_id, limit=10)
    assert reviews[0].rating == 2
