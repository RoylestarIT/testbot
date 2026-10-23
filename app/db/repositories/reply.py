from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import GeneratedReply


class ReplyRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, reply_id: int) -> GeneratedReply | None:
        return await self._session.get(GeneratedReply, reply_id)

    async def list_by_review_id(self, review_id: int) -> list[GeneratedReply]:
        result = await self._session.execute(
            select(GeneratedReply)
            .where(GeneratedReply.review_id == review_id)
            .order_by(GeneratedReply.variant_index)
        )
        return list(result.scalars().all())

    async def create(
        self,
        *,
        review_id: int,
        variant_index: int,
        text: str,
        model: str | None = None,
        tokens_used: int | None = None,
    ) -> GeneratedReply:
        reply = GeneratedReply(
            review_id=review_id,
            variant_index=variant_index,
            text=text,
            model=model,
            tokens_used=tokens_used,
        )
        self._session.add(reply)
        await self._session.flush()
        await self._session.refresh(reply)
        return reply

    async def latest_text_by_review_ids(self, review_ids: list[int]) -> dict[int, str]:
        if not review_ids:
            return {}
        subq = (
            select(
                GeneratedReply.review_id,
                func.max(GeneratedReply.id).label("max_id"),
            )
            .where(GeneratedReply.review_id.in_(review_ids))
            .group_by(GeneratedReply.review_id)
            .subquery()
        )
        result = await self._session.execute(
            select(GeneratedReply.review_id, GeneratedReply.text)
            .join(subq, GeneratedReply.id == subq.c.max_id)
        )
        return {int(row[0]): str(row[1]) for row in result.all()}
