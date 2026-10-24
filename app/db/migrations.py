import asyncio
from pathlib import Path

from alembic import command
from alembic.config import Config

from app.core.config import get_settings

_ALEMBIC_INI = Path(__file__).resolve().parents[2] / "alembic.ini"


def _sync_database_url(async_url: str) -> str:
    if "+aiosqlite" in async_url:
        return async_url.replace("+aiosqlite", "", 1)
    return async_url


def run_migrations() -> None:
    settings = get_settings()
    cfg = Config(str(_ALEMBIC_INI))
    cfg.set_main_option("sqlalchemy.url", _sync_database_url(settings.database_url))
    command.upgrade(cfg, "head")


async def run_migrations_async() -> None:
    await asyncio.to_thread(run_migrations)
