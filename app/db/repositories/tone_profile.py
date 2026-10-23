from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ToneProfile


class ToneProfileRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_by_user_id(self, user_id: int) -> list[ToneProfile]:
        result = await self._session.execute(
            select(ToneProfile)
            .where(ToneProfile.user_id == user_id)
            .order_by(ToneProfile.id)
        )
        return list(result.scalars().all())

    async def get_by_id(self, profile_id: int) -> ToneProfile | None:
        return await self._session.get(ToneProfile, profile_id)
