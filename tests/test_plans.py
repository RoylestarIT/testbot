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
    LITE_MAX_MARKETPLACE_ACCOUNTS,
    PRO_MAX_MARKETPLACE_ACCOUNTS,
    can_add_marketplace_account,
    can_add_tone_profile,
    has_unlimited_generations,
    max_marketplace_accounts,
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


async def _add_wb(session: AsyncSession, user_id: int, shop: str) -> None:
    await AccountRepository(session).create(
        user_id=user_id,
        marketplace=Marketplace.WB,
        encrypted_api_key="enc",
        shop_name=shop,
        is_active=True,
    )


@pytest.mark.asyncio
async def test_lite_user_limited_to_two_accounts(session: AsyncSession) -> None:
    user = await UserRepository(session).create(tg_id=8010, username="lite2")
    await SubscriptionRepository(session).create(
        user_id=user.id,
        plan=SubscriptionPlan.LITE,
        status=SubscriptionStatus.ACTIVE,
        expires_at=datetime.now(UTC) + timedelta(days=30),
        payment_method=PaymentMethod.STARS,
    )
    await _add_wb(session, user.id, "a1")
    await _add_wb(session, user.id, "a2")
    await session.commit()
    assert await max_marketplace_accounts(session, user.id) == LITE_MAX_MARKETPLACE_ACCOUNTS
    allowed, msg = await can_add_marketplace_account(session, user.id)
    assert allowed is False
    assert msg is not None
    assert "Lite" in msg


@pytest.mark.asyncio
async def test_pro_user_limited_to_four_accounts(session: AsyncSession) -> None:
    user = await UserRepository(session).create(tg_id=8011, username="pro4")
    await SubscriptionRepository(session).create(
        user_id=user.id,
        plan=SubscriptionPlan.PRO,
        status=SubscriptionStatus.ACTIVE,
        expires_at=datetime.now(UTC) + timedelta(days=30),
        payment_method=PaymentMethod.STARS,
    )
    for i in range(PRO_MAX_MARKETPLACE_ACCOUNTS):
        await _add_wb(session, user.id, f"s{i}")
    await session.commit()
    assert await max_marketplace_accounts(session, user.id) == PRO_MAX_MARKETPLACE_ACCOUNTS
    allowed, msg = await can_add_marketplace_account(session, user.id)
    assert allowed is False
    assert "PRO" in msg


@pytest.mark.asyncio
async def test_free_user_still_limited(session: AsyncSession) -> None:
    user = await UserRepository(session).create(tg_id=8002, username="free")
    await session.commit()
    assert await has_unlimited_generations(session, user.id) is False
    remaining = await remaining_generations_today(session, user.id)
    assert remaining == 5
