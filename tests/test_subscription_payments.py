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
from app.services.payment.telegram_stars import invoice_payload, parse_invoice_payload
from app.services.subscription import (
    activate_from_stars,
    approve_qr_subscription,
    create_qr_pending,
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


def test_invoice_payload_roundtrip() -> None:
    payload = invoice_payload(SubscriptionPlan.LITE, 42)
    assert parse_invoice_payload(payload) == (SubscriptionPlan.LITE, 42)


@pytest.mark.asyncio
async def test_activate_from_stars(session: AsyncSession) -> None:
    user = await UserRepository(session).create(tg_id=9001, username="u")
    await session.commit()
    sub = await activate_from_stars(
        session,
        user_id=user.id,
        plan=SubscriptionPlan.PRO,
        telegram_payment_charge_id="charge-1",
    )
    await session.commit()
    assert sub.status == SubscriptionStatus.ACTIVE
    assert sub.plan == SubscriptionPlan.PRO
    assert sub.payment_method == PaymentMethod.STARS
    assert sub.expires_at is not None


@pytest.mark.asyncio
async def test_qr_approve_flow(session: AsyncSession) -> None:
    user = await UserRepository(session).create(tg_id=9002, username="u2")
    pending = await create_qr_pending(session, user_id=user.id, plan=SubscriptionPlan.LITE)
    await session.commit()

    approved = await approve_qr_subscription(session, pending.id)
    await session.commit()
    assert approved is not None
    assert approved.status == SubscriptionStatus.ACTIVE

    active = await get_effective_subscription(session, user.id)
    assert active is not None
    assert active.id == pending.id


@pytest.mark.asyncio
async def test_expired_subscription_not_active(session: AsyncSession) -> None:
    user = await UserRepository(session).create(tg_id=9003, username="u3")
    repo = SubscriptionRepository(session)
    expired = await repo.create(
        user_id=user.id,
        plan=SubscriptionPlan.PRO,
        status=SubscriptionStatus.ACTIVE,
        expires_at=datetime.now(UTC) - timedelta(days=1),
        payment_method=PaymentMethod.STARS,
    )
    await session.commit()
    assert expired.id
    active = await repo.get_active_for_user(user.id)
    assert active is None
