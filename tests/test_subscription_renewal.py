from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.models import Base, PaymentMethod, SubscriptionPlan, SubscriptionStatus
from app.db.repositories.subscription import SubscriptionRepository
from app.db.repositories.user import UserRepository
from app.services.subscription import (
    SUBSCRIPTION_PERIOD_DAYS,
    activate_from_stars,
    get_effective_subscription,
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


def _utc(value: datetime) -> datetime:
    return value if value.tzinfo else value.replace(tzinfo=UTC)


async def _active(session: AsyncSession, user_id: int, plan: SubscriptionPlan, days_left: int):
    return await SubscriptionRepository(session).create(
        user_id=user_id,
        plan=plan,
        status=SubscriptionStatus.ACTIVE,
        expires_at=datetime.now(UTC) + timedelta(days=days_left),
        payment_method=PaymentMethod.STARS,
    )


async def test_same_plan_renewal_keeps_remaining_days(session: AsyncSession) -> None:
    user = await UserRepository(session).create(tg_id=7001)
    old = await _active(session, user.id, SubscriptionPlan.PRO, days_left=20)
    await session.commit()

    renewed = await activate_from_stars(
        session, user_id=user.id, plan=SubscriptionPlan.PRO, telegram_payment_charge_id="c1"
    )
    await session.commit()

    expected = _utc(old.expires_at) + timedelta(days=SUBSCRIPTION_PERIOD_DAYS)
    assert abs(_utc(renewed.expires_at) - expected) < timedelta(seconds=5)
    await session.refresh(old)
    assert old.status == SubscriptionStatus.EXPIRED


async def test_plan_change_starts_from_now(session: AsyncSession) -> None:
    user = await UserRepository(session).create(tg_id=7002)
    await _active(session, user.id, SubscriptionPlan.LITE, days_left=20)
    await session.commit()

    upgraded = await activate_from_stars(
        session, user_id=user.id, plan=SubscriptionPlan.PRO, telegram_payment_charge_id="c2"
    )
    await session.commit()

    expected = datetime.now(UTC) + timedelta(days=SUBSCRIPTION_PERIOD_DAYS)
    assert abs(_utc(upgraded.expires_at) - expected) < timedelta(seconds=5)


async def test_first_purchase_starts_from_now(session: AsyncSession) -> None:
    user = await UserRepository(session).create(tg_id=7003)
    await session.commit()

    sub = await activate_from_stars(
        session, user_id=user.id, plan=SubscriptionPlan.LITE, telegram_payment_charge_id="c3"
    )
    await session.commit()

    expected = datetime.now(UTC) + timedelta(days=SUBSCRIPTION_PERIOD_DAYS)
    assert abs(_utc(sub.expires_at) - expected) < timedelta(seconds=5)


async def test_effective_subscription_tolerates_duplicate_active_rows(session: AsyncSession) -> None:
    user = await UserRepository(session).create(tg_id=7004)
    await _active(session, user.id, SubscriptionPlan.PRO, days_left=5)
    newest = await _active(session, user.id, SubscriptionPlan.PRO, days_left=10)
    await session.commit()

    effective = await get_effective_subscription(session, user.id)
    assert effective is not None
    assert effective.id == newest.id
