from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

import app.services.payment.crypto_pay as crypto_pay
import app.tasks.crypto_pay_poller as crypto_poller
from app.core.config import Settings
from app.db.models import Base, SubscriptionPlan, SubscriptionStatus
from app.db.repositories.subscription import SubscriptionRepository
from app.db.repositories.user import UserRepository
from app.services.subscription import create_crypto_pending


@pytest.fixture
async def factory(tmp_path, monkeypatch: pytest.MonkeyPatch):
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'crypto.db'}")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    monkeypatch.setattr(crypto_poller, "get_session_factory", lambda: session_factory)
    yield session_factory
    await engine.dispose()


def _settings() -> Settings:
    return Settings(_env_file=None, BOT_TOKEN="x", CRYPTO_PAY_API_TOKEN="t")


async def _pending(factory, invoice_ids: list[str]) -> list[int]:
    async with factory() as session:
        user = await UserRepository(session).create(tg_id=6601)
        ids = []
        for invoice_id in invoice_ids:
            sub = await create_crypto_pending(session, user_id=user.id, plan=SubscriptionPlan.PRO)
            sub.external_payment_id = invoice_id
            await session.flush()
            ids.append(sub.id)
        await session.commit()
        return ids


async def test_poller_uses_single_batch_call_and_settles_rows(factory, monkeypatch) -> None:
    paid_id, expired_id, active_id = await _pending(factory, ["11", "12", "13"])
    api = AsyncMock(
        return_value={
            "items": [
                {"invoice_id": 11, "status": "paid"},
                {"invoice_id": 12, "status": "expired"},
                {"invoice_id": 13, "status": "active"},
            ]
        }
    )
    monkeypatch.setattr(crypto_pay, "_api_request", api)
    bot = AsyncMock()

    await crypto_poller.process_crypto_pending_once(bot, _settings())

    api.assert_awaited_once()
    assert api.await_args.kwargs["invoice_ids"] == "11,12,13"
    async with factory() as session:
        repo = SubscriptionRepository(session)
        assert (await repo.get_by_id(paid_id)).status == SubscriptionStatus.ACTIVE
        assert (await repo.get_by_id(expired_id)).status == SubscriptionStatus.EXPIRED
        assert (await repo.get_by_id(active_id)).status == SubscriptionStatus.PENDING
    bot.send_message.assert_awaited_once()


async def test_poller_skips_when_api_fails(factory, monkeypatch) -> None:
    (sub_id,) = await _pending(factory, ["21"])
    monkeypatch.setattr(
        crypto_pay, "_api_request", AsyncMock(side_effect=crypto_pay.CryptoPayError("down"))
    )

    await crypto_poller.process_crypto_pending_once(AsyncMock(), _settings())

    async with factory() as session:
        assert (await SubscriptionRepository(session).get_by_id(sub_id)).status == SubscriptionStatus.PENDING


async def test_get_invoices_batches_by_100(monkeypatch) -> None:
    api = AsyncMock(return_value={"items": []})
    monkeypatch.setattr(crypto_pay, "_api_request", api)
    await crypto_pay.get_invoices(_settings(), list(range(1, 251)))
    assert api.await_count == 3
