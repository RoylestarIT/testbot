from datetime import UTC, datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.models import Base, GeneratedReply, Marketplace, Review, ReviewStatus
from app.db.repositories.account import AccountRepository
from app.db.repositories.reply import ReplyRepository
from app.db.repositories.review import ReviewRepository
from app.db.repositories.user import UserRepository
from app.services.generation_limit import (
    FREE_DAILY_GENERATIONS,
    VARIANTS_PER_GENERATION,
    can_generate,
    generations_used_from_reply_count,
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


@pytest.mark.asyncio
async def test_generations_used_from_reply_count() -> None:
    assert generations_used_from_reply_count(0) == 0
    assert generations_used_from_reply_count(3) == 1
    assert generations_used_from_reply_count(14) == 4


@pytest.mark.asyncio
async def test_free_user_blocked_after_daily_limit(session: AsyncSession) -> None:
    user = await UserRepository(session).create(tg_id=1001, username="seller")
    account = await AccountRepository(session).create(
        user_id=user.id,
        marketplace=Marketplace.WB,
        encrypted_api_key="x",
        shop_name="test",
    )
    review = await ReviewRepository(session).create(
        account_id=account.id,
        external_id="ext-1",
        rating=5,
        text="ok",
        status=ReviewStatus.NEW,
    )
    reply_repo = ReplyRepository(session)
    now = datetime.now(UTC)
    for index in range(FREE_DAILY_GENERATIONS * VARIANTS_PER_GENERATION):
        reply = GeneratedReply(
            review_id=review.id,
            variant_index=index,
            text=f"v{index}",
            created_at=now,
        )
        session.add(reply)
    await session.commit()

    allowed, message = await can_generate(session, user.id)
    assert allowed is False
    assert message is not None
