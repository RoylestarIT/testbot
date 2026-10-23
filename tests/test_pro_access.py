from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.models import Base, SubscriptionPlan, SubscriptionStatus
from app.db.repositories.subscription import SubscriptionRepository
from app.db.repositories.user import UserRepository
from app.services.pro_access import (
    activate_trial_pro,
    can_api_publish,
    consume_api_publish_quota,
    has_pro_access,
    is_trial_pro_active,
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
async def test_trial_pro_grants_access_and_publish_quota(session: AsyncSession) -> None:
    user = await UserRepository(session).create(tg_id=9001, username="trial")
    assert user.free_api_publishes_remaining == 3

    updated, err = await activate_trial_pro(session, user.id)
    assert err is None
    assert updated is not None
    assert await is_trial_pro_active(updated) is True
    assert await has_pro_access(session, user.id) is True

    allowed, reason = await can_api_publish(session, user.id)
    assert allowed is True
    assert reason == "pro"

    await consume_api_publish_quota(session, user.id)
    await session.refresh(updated)
    assert updated.free_api_publishes_remaining == 3


@pytest.mark.asyncio
async def test_free_publish_quota_without_pro(session: AsyncSession) -> None:
    user = await UserRepository(session).create(tg_id=9002, username="lite")
    user.free_api_publishes_remaining = 1
    await session.flush()

    allowed, reason = await can_api_publish(session, user.id)
    assert allowed is True
    assert reason == "free_quota"

    await consume_api_publish_quota(session, user.id)
    await session.refresh(user)
    assert user.free_api_publishes_remaining == 0

    allowed, reason = await can_api_publish(session, user.id)
    assert allowed is False
    assert reason == "need_pro"


@pytest.mark.asyncio
async def test_paid_pro_overrides_trial(session: AsyncSession) -> None:
    user = await UserRepository(session).create(tg_id=9003, username="pro")
    user.trial_pro_until = datetime.now(UTC) - timedelta(days=1)
    await session.flush()

    await SubscriptionRepository(session).create(
        user_id=user.id,
        plan=SubscriptionPlan.PRO,
        status=SubscriptionStatus.ACTIVE,
        expires_at=datetime.now(UTC) + timedelta(days=30),
    )
    await session.commit()

    assert await has_pro_access(session, user.id) is True
