import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.models import Base, Marketplace, ReviewStatus
from app.db.repositories.account import AccountRepository
from app.db.repositories.review import ReviewRepository
from app.db.repositories.user import UserRepository
from app.services.period_analytics import build_period_analytics_block, queue_negative_share


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
async def test_period_analytics_empty_user(session: AsyncSession) -> None:
    user = await UserRepository(session).create(tg_id=99001122, username="a")
    block = await build_period_analytics_block(session, user.id)
    assert "7 дней" in block or "недел" in block.lower()
    assert "очеред" in block.lower()
    low, total = await queue_negative_share(session, user.id)
    assert low == 0 and total == 0


@pytest.mark.asyncio
async def test_queue_negative_share(session: AsyncSession) -> None:
    user = await UserRepository(session).create(tg_id=99001123, username="b")
    acc = await AccountRepository(session).create(
        user_id=user.id,
        marketplace=Marketplace.WB,
        encrypted_api_key="k",
        shop_name="S",
    )
    await ReviewRepository(session).create(
        account_id=acc.id,
        external_id="e1",
        rating=2,
        text="bad",
        status=ReviewStatus.NEW,
    )
    await ReviewRepository(session).create(
        account_id=acc.id,
        external_id="e2",
        rating=5,
        text="ok",
        status=ReviewStatus.NEW,
    )
    low, total = await queue_negative_share(session, user.id)
    assert total == 2
    assert low == 1
