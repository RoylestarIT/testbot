from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Review, ReviewStatus
from app.db.repositories.reply import ReplyRepository
from app.db.repositories.review import ReviewRepository

BULK_MAX = 25


def is_bulk_eligible(review: Review) -> bool:
    if review.status != ReviewStatus.NEW:
        return False
    if review.rating is None or review.rating < 4:
        return False
    text = (review.text or "").strip()
    return len(text) < 20


async def list_bulk_eligible(session: AsyncSession, user_id: int) -> list[Review]:
    reviews = await ReviewRepository(session).list_new_for_user(user_id, limit=100)
    eligible = [r for r in reviews if is_bulk_eligible(r)]
    return eligible[:BULK_MAX]


async def apply_bulk_template(
    session: AsyncSession,
    *,
    user_id: int,
    template_text: str,
) -> int:
    reviews = await list_bulk_eligible(session, user_id)
    if not reviews:
        return 0
    reply_repo = ReplyRepository(session)
    review_repo = ReviewRepository(session)
    count = 0
    for review in reviews:
        await reply_repo.create(
            review_id=review.id,
            variant_index=0,
            text=template_text,
            model="bulk_template",
        )
        await review_repo.update_status(review.id, ReviewStatus.PROCESSED)
        count += 1
    return count
