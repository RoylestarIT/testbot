from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.models import (
    Base,
    PaymentMethod,
    SubscriptionPlan,
    SubscriptionStatus,
)
from app.db.repositories.subscription import SubscriptionRepository
from app.db.repositories.user import UserRepository
from app.services.generation_limit import can_generate, remaining_generations_today
from app.services.plans import has_unlimited_generations


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
async def test_paid_lite_unlocks_unlimited_generations(session: AsyncSession) -> None:
    user = await UserRepository(session).create(tg_id=8001, username="lite_paid")
    await SubscriptionRepository(session).create(
        user_id=user.id,
        plan=SubscriptionPlan.LITE,
        status=SubscriptionStatus.ACTIVE,
        expires_at=datetime.now(UTC) + timedelta(days=30),
        payment_method=PaymentMethod.STARS,
    )
    await session.commit()

    assert await has_unlimited_generations(session, user.id) is True
    assert await remaining_generations_today(session, user.id) is None
    allowed, msg = await can_generate(session, user.id)
    assert allowed is True
    assert msg is None


@pytest.mark.asyncio
async def test_free_user_still_limited(session: AsyncSession) -> None:
    user = await UserRepository(session).create(tg_id=8002, username="free")
    await session.commit()
    assert await has_unlimited_generations(session, user.id) is False
    remaining = await remaining_generations_today(session, user.id)
    assert remaining == 5
