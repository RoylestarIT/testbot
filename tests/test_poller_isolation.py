from unittest.mock import AsyncMock

import httpx
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

import app.tasks.poller as poller
from app.db.models import Base, Marketplace, MarketplaceAccount, Review, ReviewStatus
from app.db.repositories.account import AccountRepository
from app.db.repositories.review import ReviewRepository
from app.db.repositories.user import UserRepository
from app.services.marketplace.auto_publish_types import AutoPublishOutcome
from app.services.marketplace.base import MarketplaceAPIError


@pytest.fixture
async def factory(tmp_path, monkeypatch: pytest.MonkeyPatch):
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'poller.db'}")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    monkeypatch.setattr(poller, "get_session_factory", lambda: session_factory)
    monkeypatch.setattr(poller, "WildberriesClient", lambda: AsyncMock())
    monkeypatch.setattr(
        poller, "refresh_unanswered_questions", AsyncMock(return_value=(0, 0))
    )
    monkeypatch.setattr(
        poller, "try_auto_publish_review", AsyncMock(return_value=AutoPublishOutcome("skipped"))
    )
    yield session_factory
    await engine.dispose()


async def _seed(factory, count: int) -> list[int]:
    async with factory() as session:
        user = await UserRepository(session).create(tg_id=5551)
        ids = []
        for i in range(count):
            account = MarketplaceAccount(
                user_id=user.id,
                marketplace=Marketplace.WB,
                encrypted_api_key="x",
                shop_name=f"shop{i}",
            )
            session.add(account)
            await session.flush()
            ids.append(account.id)
        await session.commit()
        return ids


async def test_one_failing_account_does_not_block_others(factory, monkeypatch) -> None:
    ids = await _seed(factory, 3)
    broken = ids[1]

    async def fake_sync(session, account, **_kwargs):
        if account.id == broken:
            raise httpx.ReadTimeout("slow marketplace")
        review = await ReviewRepository(session).create(
            account_id=account.id, external_id=f"r{account.id}", rating=2, status=ReviewStatus.NEW
        )
        return 1, 1, [review]

    monkeypatch.setattr(poller, "sync_account_reviews", fake_sync)
    bot = AsyncMock()

    await poller.poll_marketplace_reviews_once(bot)

    async with factory() as session:
        reviews = (await session.execute(select(Review.account_id))).scalars().all()
        broken_acc = await AccountRepository(session).get_by_id(broken)
    assert sorted(reviews) == [ids[0], ids[2]]
    assert broken_acc.last_sync_error and "slow marketplace" in broken_acc.last_sync_error
    assert poller.get_poller_health()["last_error"] is None
    assert poller.get_poller_health()["failed_accounts_last_run"] == 1
    bot.send_message.assert_awaited()


async def test_auth_failure_deactivation_is_persisted(factory, monkeypatch) -> None:
    (account_id,) = await _seed(factory, 1)

    async def fake_sync(session, account, **_kwargs):
        await AccountRepository(session).set_active(account.id, False)
        account.last_sync_error = "API-ключ не принят"
        await session.flush()
        raise MarketplaceAPIError("unauthorized", status_code=401)

    monkeypatch.setattr(poller, "sync_account_reviews", fake_sync)
    bot = AsyncMock()

    await poller.poll_marketplace_reviews_once(bot)

    async with factory() as session:
        account = await AccountRepository(session).get_by_id(account_id)
    assert account.is_active is False
    assert account.last_sync_error == "API-ключ не принят"
    bot.send_message.assert_awaited()
