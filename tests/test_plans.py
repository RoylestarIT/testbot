from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.models import (
    Base,
    Marketplace,
    PaymentMethod,
    SubscriptionPlan,
    SubscriptionStatus,
)
from app.db.repositories.subscription import SubscriptionRepository
from app.db.repositories.user import UserRepository
from app.services.generation_limit import can_generate, remaining_generations_today
from app.db.repositories.account import AccountRepository
from app.db.repositories.tone_profile import ToneProfileRepository
from app.services.plans import (
    FREE_MAX_MARKETPLACE_ACCOUNTS,
    can_add_marketplace_account,
    can_add_tone_profile,
    has_unlimited_generations,
)


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
async def test_free_user_cannot_add_second_account(session: AsyncSession) -> None:
    user = await UserRepository(session).create(tg_id=8003, username="one_cab")
    await AccountRepository(session).create(
        user_id=user.id,
        marketplace=Marketplace.WB,
        encrypted_api_key="enc",
        shop_name="shop",
        is_active=True,
    )
    await session.commit()
    allowed, msg = await can_add_marketplace_account(session, user.id)
    assert allowed is False
    assert msg is not None
    assert str(FREE_MAX_MARKETPLACE_ACCOUNTS) in msg


@pytest.mark.asyncio
async def test_free_user_cannot_add_second_tone(session: AsyncSession) -> None:
    user = await UserRepository(session).create(tg_id=8004, username="one_tone")
    await ToneProfileRepository(session).create(
        user_id=user.id,
        description="friendly tone",
        example_replies=None,
    )
    await session.commit()
    allowed, msg = await can_add_tone_profile(session, user.id)
    assert allowed is False
    assert msg is not None


@pytest.mark.asyncio
async def test_free_user_still_limited(session: AsyncSession) -> None:
    user = await UserRepository(session).create(tg_id=8002, username="free")
    await session.commit()
    assert await has_unlimited_generations(session, user.id) is False
    remaining = await remaining_generations_today(session, user.id)
    assert remaining == 5
