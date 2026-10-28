import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.models import Base, Marketplace, MarketplaceAccount, User
from app.services.public_metrics import build_public_metrics


@pytest.fixture
async def session() -> AsyncSession:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        yield s
    await engine.dispose()


@pytest.mark.asyncio
async def test_build_public_metrics_counts_distinct_sellers(session: AsyncSession) -> None:
    u1 = User(tg_id=101, username="a")
    u2 = User(tg_id=102, username="b")
    session.add_all([u1, u2])
    await session.flush()
    session.add_all(
        [
            MarketplaceAccount(
                user_id=u1.id,
                marketplace=Marketplace.WB,
                shop_name="wb1",
                encrypted_api_key="enc",
            ),
            MarketplaceAccount(
                user_id=u1.id,
                marketplace=Marketplace.OZON,
                shop_name="oz1",
                encrypted_api_key="enc",
            ),
            MarketplaceAccount(
                user_id=u2.id,
                marketplace=Marketplace.WB,
                shop_name="wb2",
                encrypted_api_key="enc",
            ),
        ]
    )
    await session.commit()

    data = await build_public_metrics(session)
    assert data["telegramAccounts"] == 2
    assert data["sellersWithCabinet"] == 2
    assert data["updatedAt"]
