from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import MarketplaceAccount, Review, ReviewStatus, User
from app.db.repositories.tone_profile import ToneProfileRepository
from app.services.plans import count_user_api_accounts


def _mark(done: bool) -> str:
    return "✅" if done else "⬜️"


async def build_onboarding_checklist(session: AsyncSession, user: User) -> str:
    terms = user.terms_accepted_at is not None
    api_count = await count_user_api_accounts(session, user.id)
    cabinet = api_count > 0
    tones = await ToneProfileRepository(session).list_by_user_id(user.id)
    tone_ok = len(tones) > 0
    onboarding_done = user.onboarding_completed_at is not None

    from sqlalchemy import func, select

    first_reply_stmt = (
        select(func.count(Review.id))
        .select_from(Review)
        .join(MarketplaceAccount, Review.account_id == MarketplaceAccount.id)
        .where(
            MarketplaceAccount.user_id == user.id,
            Review.status.in_((ReviewStatus.PROCESSED, ReviewStatus.PUBLISHED)),
        )
    )
    replied = int((await session.scalar(first_reply_stmt)) or 0) > 0

    lines = [
        "<b>Чеклист старта</b>",
        f"{_mark(terms)} Приняты условия",
        f"{_mark(cabinet)} Подключён кабинет WB/Ozon",
        f"{_mark(tone_ok)} Настроен tone of voice",
        f"{_mark(replied)} Первый ответ (копирование или publish)",
        f"{_mark(onboarding_done)} Мастер «Быстрый старт»",
    ]
    if all([terms, cabinet, tone_ok, replied, onboarding_done]):
        return ""
    return "\n".join(lines) + "\n"
