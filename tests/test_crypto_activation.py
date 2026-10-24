import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.models import Base, SubscriptionPlan, SubscriptionStatus
from app.db.repositories.user import UserRepository
from app.services.subscription import activate_from_crypto_invoice, create_crypto_pending


@pytest.fixture
async def factory():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield async_sessionmaker(engine, expire_on_commit=False)
    await engine.dispose()


async def _user_id(factory) -> int:
    async with factory() as session:
        user = await UserRepository(session).create(tg_id=8101)
        await session.commit()
        return user.id


async def test_crypto_invoice_activates_only_once(factory) -> None:
    user_id = await _user_id(factory)
    async with factory() as session:
        pending = await create_crypto_pending(session, user_id=user_id, plan=SubscriptionPlan.PRO)
        pending.external_payment_id = "111"
        await session.commit()

    async with factory() as session:
        first = await activate_from_crypto_invoice(session, subscription_id=pending.id, invoice_id="111")
        await session.commit()
    async with factory() as session:
        second = await activate_from_crypto_invoice(session, subscription_id=pending.id, invoice_id="111")
        await session.commit()

    assert first is not None
    assert first.status == SubscriptionStatus.ACTIVE
    assert second is None


async def test_pending_with_invoice_is_not_reused(factory) -> None:
    user_id = await _user_id(factory)
    async with factory() as session:
        first = await create_crypto_pending(session, user_id=user_id, plan=SubscriptionPlan.LITE)
        first.external_payment_id = "201"
        await session.commit()

    async with factory() as session:
        second = await create_crypto_pending(session, user_id=user_id, plan=SubscriptionPlan.LITE)
        await session.commit()

    assert second.id != first.id

    async with factory() as session:
        activated = await activate_from_crypto_invoice(session, subscription_id=first.id, invoice_id="201")
        await session.commit()
    assert activated is not None
    assert activated.id == first.id


async def test_pending_without_invoice_is_reused(factory) -> None:
    user_id = await _user_id(factory)
    async with factory() as session:
        first = await create_crypto_pending(session, user_id=user_id, plan=SubscriptionPlan.LITE)
        await session.commit()
    async with factory() as session:
        second = await create_crypto_pending(session, user_id=user_id, plan=SubscriptionPlan.LITE)
        await session.commit()
    assert second.id == first.id
