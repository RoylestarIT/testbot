from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import MarketplaceAccount, Review, ReviewStatus, User
from app.db.repositories.tone_profile import ToneProfileRepository
from app.services.plans import count_user_api_accounts


async def build_onboarding_nudge(session: AsyncSession, user: User) -> str:
    """Короткая подсказка только по незавершённым шагам (без длинного чеклиста)."""
    pending: list[str] = []

    if await count_user_api_accounts(session, user.id) == 0:
        pending.append("подключить кабинет WB или Ozon")

    tones = await ToneProfileRepository(session).list_by_user_id(user.id)
    if not tones:
        pending.append("настроить tone of voice")

    first_reply_stmt = (
        select(func.count(Review.id))
        .select_from(Review)
        .join(MarketplaceAccount, Review.account_id == MarketplaceAccount.id)
        .where(
            MarketplaceAccount.user_id == user.id,
            Review.status.in_((ReviewStatus.PROCESSED, ReviewStatus.PUBLISHED)),
        )
    )
    if int((await session.scalar(first_reply_stmt)) or 0) == 0:
        pending.append("ответить на первый отзыв")

    if user.onboarding_completed_at is None and len(pending) > 1:
        pending.append("пройти «Быстрый старт»")

    if not pending:
        return ""

    if len(pending) == 1:
        return f"💡 Осталось: {pending[0]}."
    shown = ", ".join(pending[:2])
    extra = f" (+{len(pending) - 2})" if len(pending) > 2 else ""
    return f"💡 Дальше: {shown}{extra}."


async def build_onboarding_checklist(session: AsyncSession, user: User) -> str:
    """Сводка больше не использует длинный чеклист — см. build_onboarding_nudge."""
    return await build_onboarding_nudge(session, user)
