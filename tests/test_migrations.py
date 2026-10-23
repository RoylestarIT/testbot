import pytest
from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import get_settings
from app.db.migrations import run_migrations


@pytest.fixture
def migrated_db(tmp_path, monkeypatch: pytest.MonkeyPatch):
    db_path = tmp_path / "test.db"
    url = f"sqlite+aiosqlite:///{db_path}"
    monkeypatch.setenv("DATABASE_URL", url)
    get_settings.cache_clear()
    run_migrations()
    yield url
    get_settings.cache_clear()


def test_alembic_upgrade_creates_tables(migrated_db: str) -> None:
    sync_url = migrated_db.replace("+aiosqlite", "", 1)
    from sqlalchemy import create_engine

    engine = create_engine(sync_url)
    tables = set(inspect(engine).get_table_names())
    engine.dispose()
    assert {
        "users",
        "marketplace_accounts",
        "reviews",
        "generated_replies",
        "subscriptions",
        "tone_profiles",
        "alembic_version",
    } <= tables


@pytest.mark.asyncio
async def test_user_repository_after_migration(migrated_db: str) -> None:
    from sqlalchemy.ext.asyncio import async_sessionmaker

    engine = create_async_engine(migrated_db)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        from app.db.repositories import UserRepository

        repo = UserRepository(session)
        user, created = await repo.get_or_create(tg_id=42, username="seller")
        assert created is True
        assert user.tg_id == 42
        await session.commit()

    async with session_factory() as session:
        result = await session.execute(text("SELECT COUNT(*) FROM users"))
        assert result.scalar_one() == 1
    await engine.dispose()
