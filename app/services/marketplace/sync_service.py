from __future__ import annotations

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import MarketplaceAccount, ReviewStatus
from app.db.repositories.review import ReviewRepository
from app.services.marketplace.base import MarketplaceAPIError, MarketplaceClient
from app.services.marketplace.factory import get_client_for_account


async def sync_account_reviews(
    session: AsyncSession,
    account: MarketplaceAccount,
    *,
    limit: int = 50,
    client: MarketplaceClient | None = None,
) -> tuple[int, int]:
    """Возвращает (новых, всего обработано)."""
    marketplace_client = client or get_client_for_account(account)
    own_client = client is None
    try:
        dtos = await marketplace_client.fetch_reviews(account, limit=limit, unanswered_only=True)
    finally:
        if own_client and hasattr(marketplace_client, "aclose"):
            await marketplace_client.aclose()

    repo = ReviewRepository(session)
    created = 0
    for dto in dtos:
        if not dto.external_id:
            continue
        existing = await repo.get_by_external_id(account.id, dto.external_id)
        if existing is not None:
            continue
        await repo.create(
            account_id=account.id,
            external_id=dto.external_id,
            rating=dto.rating,
            text=dto.text,
            author=dto.author,
            status=ReviewStatus.NEW,
            raw_json=dto.raw_json,
        )
        created += 1
    logger.info(
        "Synced marketplace reviews account_id={} created={} fetched={}",
        account.id,
        created,
        len(dtos),
    )
    return created, len(dtos)
