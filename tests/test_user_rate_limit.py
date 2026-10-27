import pytest

from app.core.config import Settings
from app.services.user_rate_limit import check_and_record, reset_all_for_tests


@pytest.fixture(autouse=True)
def _clear_limits() -> None:
    reset_all_for_tests()
    yield
    reset_all_for_tests()


@pytest.mark.asyncio
async def test_sync_limit_blocks_after_cap() -> None:
    settings = Settings(_env_file=None, BOT_TOKEN="x", RATE_LIMIT_SYNC_PER_HOUR=2)
    uid = 42
    assert (await check_and_record(uid, "sync", settings=settings))[0] is True
    assert (await check_and_record(uid, "sync", settings=settings))[0] is True
    allowed, msg = await check_and_record(uid, "sync", settings=settings)
    assert allowed is False
    assert msg is not None
    assert "Обновление" in msg


@pytest.mark.asyncio
async def test_generation_respects_custom_limit() -> None:
    settings = Settings(_env_file=None, BOT_TOKEN="x")
    uid = 7
    for _ in range(3):
        assert (await check_and_record(uid, "generation", limit=3, settings=settings))[0] is True
    allowed, msg = await check_and_record(uid, "generation", limit=3, settings=settings)
    assert allowed is False
    assert "Подготовка" in msg
