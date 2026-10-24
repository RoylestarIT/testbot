from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.models import SubscriptionPlan, SubscriptionStatus, User
from app.db.repositories.subscription import SubscriptionRepository
from app.db.repositories.user import UserRepository


async def has_paid_pro(session: AsyncSession, user_id: int) -> bool:
    subscription = await SubscriptionRepository(session).get_active_for_user(user_id)
    if subscription is None or subscription.status != SubscriptionStatus.ACTIVE:
        return False
    return subscription.plan == SubscriptionPlan.PRO


def trial_pro_active(user: User | None) -> bool:
    if user is None or user.trial_pro_until is None:
        return False
    until = user.trial_pro_until
    if until.tzinfo is None:
        until = until.replace(tzinfo=UTC)
    return until > datetime.now(UTC)


async def is_trial_pro_active(user: User | None) -> bool:
    return trial_pro_active(user)


async def has_pro_access(session: AsyncSession, user_id: int) -> bool:
    if await has_paid_pro(session, user_id):
        return True
    user = await UserRepository(session).get_by_id(user_id)
    return await is_trial_pro_active(user)


async def can_api_publish(session: AsyncSession, user_id: int) -> tuple[bool, str]:
    """Можно ли публиковать в API (paid/trial PRO или бесплатные publish)."""
    if await has_pro_access(session, user_id):
        return True, "pro"
    user = await UserRepository(session).get_by_id(user_id)
    if user is not None and user.free_api_publishes_remaining > 0:
        return True, "free_quota"
    return False, "need_pro"


async def consume_api_publish_quota(session: AsyncSession, user_id: int) -> None:
    if await has_pro_access(session, user_id):
        return
    user = await UserRepository(session).get_by_id(user_id)
    if user is None or user.free_api_publishes_remaining <= 0:
        return
    user.free_api_publishes_remaining -= 1
    await session.flush()


async def activate_trial_pro(session: AsyncSession, user_id: int) -> tuple[User | None, str | None]:
    settings = get_settings()
    user = await UserRepository(session).get_by_id(user_id)
    if user is None:
        return None, "Пользователь не найден"
    if user.trial_pro_used:
        return None, "Пробный PRO уже использован"
    if await has_paid_pro(session, user_id):
        return None, "У вас уже есть активная PRO-подписка"
    user.trial_pro_used = True
    user.trial_pro_until = datetime.now(UTC) + timedelta(days=settings.trial_pro_days)
    if user.free_api_publishes_remaining < settings.free_api_publishes:
        user.free_api_publishes_remaining = settings.free_api_publishes
    await session.flush()
    return user, None


async def admin_extend_trial(session: AsyncSession, user_id: int, days: int) -> User | None:
    user = await UserRepository(session).get_by_id(user_id)
    if user is None:
        return None
    base = user.trial_pro_until or datetime.now(UTC)
    if base.tzinfo is None:
        base = base.replace(tzinfo=UTC)
    if base < datetime.now(UTC):
        base = datetime.now(UTC)
    user.trial_pro_until = base + timedelta(days=days)
    user.trial_pro_used = True
    await session.flush()
    return user
