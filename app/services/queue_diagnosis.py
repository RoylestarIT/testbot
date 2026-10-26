from __future__ import annotations

from datetime import UTC, datetime, timedelta
from enum import Enum

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.datetime_utils import as_utc
from app.db.repositories.account import AccountRepository
from app.db.repositories.review import ReviewRepository
from app.services.plans import count_user_api_accounts


class EmptyQueueReason(str, Enum):
    NO_CABINETS = "no_cabinets"
    SYNC_ERROR = "sync_error"
    NEEDS_SYNC = "needs_sync"
    ALL_DONE = "all_done"


async def diagnose_empty_queue(session: AsyncSession, user_id: int) -> EmptyQueueReason:
    if await count_user_api_accounts(session, user_id) == 0:
        return EmptyQueueReason.NO_CABINETS

    accounts = await AccountRepository(session).list_by_user_id(user_id, active_only=True)
    if any(a.last_sync_error for a in accounts):
        return EmptyQueueReason.SYNC_ERROR

    reviews = await ReviewRepository(session).list_new_for_user(user_id, limit=1)
    if reviews:
        return EmptyQueueReason.ALL_DONE

    now = datetime.now(UTC)
    synced_recently = any(
        as_utc(a.last_sync_at) is not None and as_utc(a.last_sync_at) >= now - timedelta(hours=3)
        for a in accounts
    )
    if not synced_recently:
        return EmptyQueueReason.NEEDS_SYNC
    return EmptyQueueReason.ALL_DONE
