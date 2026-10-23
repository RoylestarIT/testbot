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

    async def create(
        self,
        *,
        user_id: int,
        description: str | None,
        example_replies: list[str] | None = None,
    ) -> ToneProfile:
        profile = ToneProfile(
            user_id=user_id,
            description=description,
            example_replies=example_replies,
        )
        self._session.add(profile)
        await self._session.flush()
        await self._session.refresh(profile)
        return profile

    async def delete(self, profile_id: int, user_id: int) -> bool:
        profile = await self.get_by_id(profile_id)
        if profile is None or profile.user_id != user_id:
            return False
        await self._session.delete(profile)
        await self._session.flush()
        return True

    async def update_description(
        self,
        profile_id: int,
        user_id: int,
        *,
        description: str,
        example_replies: list[str] | None = None,
    ) -> ToneProfile | None:
        profile = await self.get_by_id(profile_id)
        if profile is None or profile.user_id != user_id:
            return None
        profile.description = description
        if example_replies is not None:
            profile.example_replies = example_replies
        await self._session.flush()
        return profile

    async def set_default(self, profile_id: int, user_id: int) -> ToneProfile | None:
        profiles = await self.list_by_user_id(user_id)
        target = await self.get_by_id(profile_id)
        if target is None or target.user_id != user_id:
            return None
        for profile in profiles:
            profile.is_default = profile.id == profile_id
        await self._session.flush()
        return target
