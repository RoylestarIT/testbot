from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.bot.ui import REVIEWS_HUB_BUTTON

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.db.models import MarketplaceAccount, ReviewStatus
from app.services.marketplace.auto_publish import try_auto_publish_review
from app.services.marketplace.sync_service import sync_account_reviews


def connect_success_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=REVIEWS_HUB_BUTTON, callback_data="review:mp:list")],
            [InlineKeyboardButton(text="⚙️ Настройки", callback_data="menu:settings")],
        ]
    )


async def sync_new_account_reviews(
    session: AsyncSession,
    account: MarketplaceAccount,
    *,
    settings: Settings | None = None,
) -> tuple[int, int, int]:
    """Первый sync после подключения + авто-публикация PRO. Возвращает (новых, авто, в очереди)."""
    settings = settings or get_settings()
    _, _, new_reviews = await sync_account_reviews(session, account)
    auto = 0
    in_queue = 0
    for review in new_reviews:
        outcome = await try_auto_publish_review(
            session, account=account, review=review, settings=settings
        )
        if outcome.status == "published":
            auto += 1
            continue
        await session.refresh(review)
        if review.status == ReviewStatus.NEW:
            in_queue += 1
    return len(new_reviews), auto, in_queue
