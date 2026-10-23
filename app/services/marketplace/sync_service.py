from __future__ import annotations

from datetime import UTC, datetime

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import MarketplaceAccount, Review, ReviewStatus
from app.db.repositories.account import AccountRepository
from app.db.repositories.review import ReviewRepository
from app.services.marketplace.base import MarketplaceAPIError, MarketplaceClient
from app.services.marketplace.factory import get_client_for_account


async def sync_account_reviews(
    session: AsyncSession,
    account: MarketplaceAccount,
    *,
    limit: int = 100,
    client: MarketplaceClient | None = None,
) -> tuple[int, int, list[Review]]:
    """Возвращает (новых, всего получено из API, созданные Review)."""
    marketplace_client = client or get_client_for_account(account)
    # Закрываем только клиенты, созданные снаружи для тестов (не shared pool).
    own_client = client is not None and getattr(marketplace_client, "_owns_client", False)
    try:
        dtos = await marketplace_client.fetch_reviews(account, limit=limit, unanswered_only=True)
    except MarketplaceAPIError as exc:
        if exc.status_code == 401:
            await AccountRepository(session).set_active(account.id, False)
            account.last_sync_error = "API-ключ не принят"
            logger.warning("Deactivated account_id={} after 401", account.id)
        else:
            account.last_sync_error = str(exc)[:500]
        await session.flush()
        raise
    finally:
        if own_client:
            await marketplace_client.aclose()

    repo = ReviewRepository(session)
    created_reviews: list[Review] = []
    for dto in dtos:
        if not dto.external_id:
            continue
        existing = await repo.get_by_external_id(account.id, dto.external_id)
        if existing is not None:
            continue
        review = await repo.create(
            account_id=account.id,
            external_id=dto.external_id,
            rating=dto.rating,
            text=dto.text,
            author=dto.author,
            status=ReviewStatus.NEW,
            raw_json=dto.raw_json,
        )
        created_reviews.append(review)

    account.last_sync_at = datetime.now(UTC)
    account.last_sync_error = None
    await session.flush()

    logger.info(
        "Synced marketplace reviews account_id={} created={} fetched={}",
        account.id,
        len(created_reviews),
        len(dtos),
    )
    return len(created_reviews), len(dtos), created_reviews
