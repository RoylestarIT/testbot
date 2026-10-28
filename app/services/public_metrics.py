from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Marketplace, MarketplaceAccount, User


async def build_public_metrics(session: AsyncSession) -> dict[str, object]:
    """Агрегаты для лендинга — без персональных данных."""
    telegram_accounts = await session.scalar(select(func.count()).select_from(User)) or 0
    sellers_with_cabinet = await session.scalar(
        select(func.count(func.distinct(MarketplaceAccount.user_id)))
        .select_from(MarketplaceAccount)
        .where(MarketplaceAccount.marketplace.in_((Marketplace.WB, Marketplace.OZON)))
    ) or 0

    return {
        "sellersWithCabinet": int(sellers_with_cabinet),
        "telegramAccounts": int(telegram_accounts),
        "updatedAt": datetime.now(UTC).replace(microsecond=0).isoformat(),
    }
