from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, user_id: int) -> User | None:
        return await self._session.get(User, user_id)

    async def map_by_ids(self, user_ids: list[int]) -> dict[int, User]:
        if not user_ids:
            return {}
        result = await self._session.execute(select(User).where(User.id.in_(user_ids)))
        return {user.id: user for user in result.scalars().all()}

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

    async def complete_onboarding(self, user_id: int) -> User | None:
        user = await self.get_by_id(user_id)
        if user is None:
            return None
        user.onboarding_completed_at = datetime.now(UTC)
        await self._session.flush()
        return user

    async def get_by_username(self, username: str) -> User | None:
        clean = username.lstrip("@").lower()
        result = await self._session.execute(select(User).where(User.username.isnot(None)))
        for user in result.scalars().all():
            if user.username and user.username.lower() == clean:
                return user
        return None

    async def set_notification_prefs(
        self,
        user_id: int,
        *,
        notify_new_reviews: bool | None = None,
        notify_negative_only: bool | None = None,
        notify_daily_digest: bool | None = None,
        notify_stale_reviews: bool | None = None,
        notify_buyer_questions: bool | None = None,
        soft_product_recommend: bool | None = None,
    ) -> User | None:
        user = await self.get_by_id(user_id)
        if user is None:
            return None
        if notify_new_reviews is not None:
            user.notify_new_reviews = notify_new_reviews
        if notify_negative_only is not None:
            user.notify_negative_only = notify_negative_only
        if notify_daily_digest is not None:
            user.notify_daily_digest = notify_daily_digest
        if notify_stale_reviews is not None:
            user.notify_stale_reviews = notify_stale_reviews
        if notify_buyer_questions is not None:
            user.notify_buyer_questions = notify_buyer_questions
        if soft_product_recommend is not None:
            user.soft_product_recommend = soft_product_recommend
        await self._session.flush()
        return user

    async def set_product_news_seen(self, user_id: int, version: str) -> User | None:
        user = await self.get_by_id(user_id)
        if user is None:
            return None
        user.product_news_seen_version = version.strip()
        await self._session.flush()
        return user

    async def set_calc_preset_volume(self, user_id: int, volume: int) -> User | None:
        user = await self.get_by_id(user_id)
        if user is None:
            return None
        user.calc_preset_volume = max(1, volume)
        await self._session.flush()
        return user

    async def accept_terms(self, user_id: int) -> User | None:
        user = await self.get_by_id(user_id)
        if user is None:
            return None
        user.terms_accepted_at = datetime.now(UTC)
        await self._session.flush()
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
