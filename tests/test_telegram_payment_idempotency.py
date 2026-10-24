import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.models import Base, PaymentMethod, Subscription, SubscriptionPlan
from app.db.repositories.subscription import SubscriptionRepository
from app.db.repositories.user import UserRepository
from app.services.subscription import activate_from_stars, grant_subscription_by_tg_id


@pytest.fixture
async def session() -> AsyncSession:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        yield session
    await engine.dispose()


async def _count(session: AsyncSession) -> int:
    return (await session.execute(select(func.count()).select_from(Subscription))).scalar_one()


async def test_redelivered_charge_does_not_create_second_subscription(session: AsyncSession) -> None:
    user = await UserRepository(session).create(tg_id=8201)
    await session.commit()

    first = await activate_from_stars(
        session, user_id=user.id, plan=SubscriptionPlan.PRO, telegram_payment_charge_id="dup-1"
    )
    await session.commit()
    second = await activate_from_stars(
        session, user_id=user.id, plan=SubscriptionPlan.PRO, telegram_payment_charge_id="dup-1"
    )
    await session.commit()

    assert second.id == first.id
    assert second.expires_at == first.expires_at
    assert await _count(session) == 1


async def test_unique_index_rejects_duplicate_charge_at_db_level(session: AsyncSession) -> None:
    user = await UserRepository(session).create(tg_id=8202)
    repo = SubscriptionRepository(session)
    from app.db.models import SubscriptionStatus

    await repo.create(
        user_id=user.id,
        plan=SubscriptionPlan.LITE,
        status=SubscriptionStatus.ACTIVE,
        payment_method=PaymentMethod.STARS,
        external_payment_id="raw-dup",
    )
    await session.commit()
    with pytest.raises(Exception):
        await repo.create(
            user_id=user.id,
            plan=SubscriptionPlan.LITE,
            status=SubscriptionStatus.ACTIVE,
            payment_method=PaymentMethod.TELEGRAM,
            external_payment_id="raw-dup",
        )
    await session.rollback()


async def test_admin_grants_are_not_constrained(session: AsyncSession) -> None:
    await UserRepository(session).create(tg_id=8203)
    await session.commit()
    for _ in range(2):
        sub, err = await grant_subscription_by_tg_id(session, tg_id=8203, plan=SubscriptionPlan.PRO)
        await session.commit()
        assert err is None and sub is not None
