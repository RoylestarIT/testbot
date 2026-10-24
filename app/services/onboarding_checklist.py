from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.ui import muted
from app.constants import MANUAL_SHOP_NAME
from app.db.models import Marketplace, MarketplaceAccount, Review, ReviewStatus, User
from app.db.repositories.account import AccountRepository
from app.db.repositories.tone_profile import ToneProfileRepository
from app.services.plans import count_user_api_accounts


async def onboarding_step_states(session: AsyncSession, user: User) -> list[tuple[str, bool]]:
    has_cabinet = await count_user_api_accounts(session, user.id) > 0
    accounts = await AccountRepository(session).list_by_user_id(user.id, active_only=True)
    api_accounts = [
        a
        for a in accounts
        if a.marketplace in (Marketplace.WB, Marketplace.OZON)
        and (a.shop_name is None or a.shop_name != MANUAL_SHOP_NAME)
    ]
    has_sync = any(a.last_sync_at is not None for a in api_accounts)
    tones = await ToneProfileRepository(session).list_by_user_id(user.id)
    has_tone = bool(tones)

    first_reply_stmt = (
        select(func.count(Review.id))
        .select_from(Review)
        .join(MarketplaceAccount, Review.account_id == MarketplaceAccount.id)
        .where(
            MarketplaceAccount.user_id == user.id,
            Review.status.in_((ReviewStatus.PROCESSED, ReviewStatus.PUBLISHED)),
        )
    )
    has_reply = int((await session.scalar(first_reply_stmt)) or 0) > 0

    return [
        ("Подключить кабинет WB или Ozon", has_cabinet),
        ("Синхронизировать отзывы (Sync)", has_sync),
        ("Настроить тон ответа", has_tone),
        ("Ответить на первый отзыв", has_reply),
    ]


async def onboarding_is_complete(session: AsyncSession, user: User) -> bool:
    steps = await onboarding_step_states(session, user)
    return all(done for _, done in steps)


async def build_onboarding_checklist_block(session: AsyncSession, user: User) -> str:
    if user.onboarding_completed_at is not None:
        return ""
    steps = await onboarding_step_states(session, user)
    if all(done for _, done in steps):
        return muted("✅ Быстрый старт: все шаги выполнены — можно закрыть в «🚀 Начать настройку».")
    lines = ["📋 <b>Быстрый старт</b>"]
    for label, done in steps:
        mark = "✅" if done else "⬜"
        lines.append(f"{mark}  {label}")
    lines.append(muted("🚀 Начать настройку — пошаговый мастер."))
    return "\n".join(lines)


async def build_onboarding_nudge(session: AsyncSession, user: User) -> str:
    """Короткая подсказка только по незавершённым шагам."""
    if user.onboarding_completed_at is not None:
        return ""
    pending: list[str] = []
    for label, done in await onboarding_step_states(session, user):
        if not done:
            pending.append(label.lower())

    if not pending:
        return ""

    if len(pending) == 1:
        return f"💡 Осталось: {pending[0]}."
    shown = ", ".join(pending[:2])
    extra = f" (+{len(pending) - 2})" if len(pending) > 2 else ""
    return f"💡 Дальше: {shown}{extra}."


async def build_onboarding_checklist(session: AsyncSession, user: User) -> str:
    return await build_onboarding_nudge(session, user)
