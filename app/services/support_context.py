from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User
from app.db.repositories.account import AccountRepository
from app.services.plans import describe_access_tier
from app.services.subscription import get_effective_subscription
from app.tasks.poller import get_poller_status_line


async def build_support_user_card(session: AsyncSession, user: User) -> str:
    subscription = await get_effective_subscription(session, user.id)
    tier = await describe_access_tier(session, user, subscription)
    accounts = await AccountRepository(session).list_by_user_id(user.id, active_only=False)
    sync_issues = sum(1 for a in accounts if a.last_sync_error)
    return (
        f"<b>Обращение из бота</b>\n"
        f"User id: <code>{user.id}</code>\n"
        f"Telegram: <code>{user.tg_id}</code> @{user.username or '—'}\n"
        f"Тариф: {tier}\n"
        f"Кабинетов: {len(accounts)} · с ошибкой sync: {sync_issues}\n"
        f"Poller: {get_poller_status_line()}"
    )
