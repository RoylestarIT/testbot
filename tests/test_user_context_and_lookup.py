from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

import app.bot.middlewares.user_context as user_context
from app.db.models import Base
from app.db.repositories.user import UserRepository


@pytest.fixture
async def factory(tmp_path, monkeypatch: pytest.MonkeyPatch):
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'uc.db'}")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    monkeypatch.setattr(user_context, "get_session_factory", lambda: session_factory)
    yield session_factory
    await engine.dispose()


async def test_get_by_username_is_case_insensitive(factory) -> None:
    async with factory() as session:
        repo = UserRepository(session)
        await repo.create(tg_id=1, username="SellerOne")
        await repo.create(tg_id=2, username=None)
        await session.commit()
        found = await repo.get_by_username("@sellerone")
        missing = await repo.get_by_username("nobody")
    assert found is not None and found.tg_id == 1
    assert missing is None


async def test_middleware_persists_new_user(factory) -> None:
    tg_user = MagicMock(id=4242, username="new_seller")
    handler = AsyncMock(return_value="ok")
    data = {"event_from_user": tg_user}

    result = await user_context.UserContextMiddleware()(handler, MagicMock(), data)

    assert result == "ok"
    assert data["db_user"].tg_id == 4242
    async with factory() as session:
        assert await UserRepository(session).get_by_tg_id(4242) is not None


async def test_middleware_does_not_answer_callback_on_db_error(monkeypatch) -> None:
    def broken_factory():
        raise RuntimeError("db down")

    monkeypatch.setattr(user_context, "get_session_factory", broken_factory)
    from aiogram.types import CallbackQuery

    event = MagicMock(spec=CallbackQuery)
    event.answer = AsyncMock()
    data = {"event_from_user": MagicMock(id=1, username=None)}

    with pytest.raises(RuntimeError):
        await user_context.UserContextMiddleware()(AsyncMock(), event, data)
    event.answer.assert_not_awaited()
