from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import MarketplaceAccount, Review, ReviewStatus
from app.services.plans import has_lite_or_higher


async def count_closed_reviews(session: AsyncSession, user_id: int) -> int:
    stmt = (
        select(func.count(Review.id))
        .select_from(Review)
        .join(MarketplaceAccount, Review.account_id == MarketplaceAccount.id)
        .where(
            MarketplaceAccount.user_id == user_id,
            Review.status.in_((ReviewStatus.PROCESSED, ReviewStatus.PUBLISHED)),
        )
    )
    return int((await session.scalar(stmt)) or 0)


def upsell_after_first_reply_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💎 Подписка", callback_data="menu:subscription")],
        ]
    )


async def first_reply_upsell_suffix(session: AsyncSession, user_id: int) -> str | None:
    if await has_lite_or_higher(session, user_id):
        return None
    if await count_closed_reviews(session, user_id) != 1:
        return None
    return (
        "\n\n🎉 <b>Первый ответ готов!</b>\n"
        "<i>PRO — publish в WB/Ozon из бота и авто только на 4–5★.</i>"
    )
