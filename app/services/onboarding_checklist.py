from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.ui import checklist_line, section
from app.db.models import MarketplaceAccount, Review, ReviewStatus, User
from app.db.repositories.tone_profile import ToneProfileRepository
from app.services.plans import count_user_api_accounts


async def build_onboarding_checklist(session: AsyncSession, user: User) -> str:
    terms = user.terms_accepted_at is not None
    api_count = await count_user_api_accounts(session, user.id)
    cabinet = api_count > 0
    tones = await ToneProfileRepository(session).list_by_user_id(user.id)
    tone_ok = len(tones) > 0
    onboarding_done = user.onboarding_completed_at is not None

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

    if all([terms, cabinet, tone_ok, replied, onboarding_done]):
        return ""

    lines = [
        section("Первые шаги"),
        checklist_line(terms, "Условия приняты"),
        checklist_line(cabinet, "Кабинет WB/Ozon"),
        checklist_line(tone_ok, "Tone of voice"),
        checklist_line(replied, "Первый ответ"),
        checklist_line(onboarding_done, "Быстрый старт"),
        "",
    ]
    return "\n".join(lines)
