from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import GeneratedReply, MarketplaceAccount, Review
from app.services.pro_access import has_pro_access

FREE_DAILY_GENERATIONS = 5
VARIANTS_PER_GENERATION = 3


async def is_pro_user(session: AsyncSession, user_id: int) -> bool:
    """PRO-возможности: оплаченный PRO или активный trial."""
    return await has_pro_access(session, user_id)


async def count_replies_today(session: AsyncSession, user_id: int) -> int:
    day_start = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
    stmt = (
        select(func.count(GeneratedReply.id))
        .select_from(GeneratedReply)
        .join(Review, GeneratedReply.review_id == Review.id)
        .join(MarketplaceAccount, Review.account_id == MarketplaceAccount.id)
        .where(
            MarketplaceAccount.user_id == user_id,
            GeneratedReply.created_at >= day_start,
        )
    )
    result = await session.execute(stmt)
    return int(result.scalar_one())


def generations_used_from_reply_count(reply_count: int) -> int:
    return reply_count // VARIANTS_PER_GENERATION


async def generations_used_today(session: AsyncSession, user_id: int) -> int:
    return generations_used_from_reply_count(await count_replies_today(session, user_id))


async def can_generate(session: AsyncSession, user_id: int) -> tuple[bool, str | None]:
    if await is_pro_user(session, user_id):
        return True, None
    used = await generations_used_today(session, user_id)
    if used >= FREE_DAILY_GENERATIONS:
        return False, (
            f"Лимит Lite: {FREE_DAILY_GENERATIONS} генераций в день исчерпан. "
            "Оформите PRO в разделе «Подписка» или попробуйте завтра."
        )
    return True, None


async def remaining_generations_today(session: AsyncSession, user_id: int) -> int | None:
    if await is_pro_user(session, user_id):
        return None
    used = await generations_used_today(session, user_id)
    return max(FREE_DAILY_GENERATIONS - used, 0)
