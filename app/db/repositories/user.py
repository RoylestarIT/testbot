from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, user_id: int) -> User | None:
        return await self._session.get(User, user_id)

    async def get_by_tg_id(self, tg_id: int) -> User | None:
        result = await self._session.execute(select(User).where(User.tg_id == tg_id))
        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        tg_id: int,
        username: str | None = None,
        is_admin: bool = False,
    ) -> User:
        user = User(tg_id=tg_id, username=username, is_admin=is_admin)
        self._session.add(user)
        await self._session.flush()
        await self._session.refresh(user)
        return user

    async def get_or_create(
        self,
        *,
        tg_id: int,
        username: str | None = None,
        is_admin: bool = False,
    ) -> tuple[User, bool]:
        existing = await self.get_by_tg_id(tg_id)
        if existing is not None:
            if username is not None and existing.username != username:
                existing.username = username
                await self._session.flush()
            return existing, False
        user = await self.create(tg_id=tg_id, username=username, is_admin=is_admin)
        return user, True
