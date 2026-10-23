from __future__ import annotations

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Marketplace, Review, ReviewStatus
from app.db.repositories.account import AccountRepository
from app.db.repositories.review import ReviewRepository
from app.services.marketplace.base import MarketplaceAPIError
from app.services.marketplace.factory import get_client_for_account
from app.services.pro_access import consume_api_publish_quota


async def publish_reply_to_marketplace(
    session: AsyncSession,
    review: Review,
    text: str,
) -> None:
    """Публикует ответ на маркетплейс после подтверждения пользователя."""
    if review.status == ReviewStatus.PUBLISHED:
        raise MarketplaceAPIError("Ответ уже опубликован ранее")

    account = await AccountRepository(session).get_by_id(review.account_id)
    if account is None or not account.is_active:
        raise MarketplaceAPIError("Аккаунт маркетплейса не найден или отключён")

    if account.marketplace not in (Marketplace.WB, Marketplace.OZON):
        raise MarketplaceAPIError("Публикация доступна только для WB и Ozon")

    client = get_client_for_account(account)
    try:
        await client.publish_reply(account, review.external_id, text)
    except MarketplaceAPIError as exc:
        logger.warning(
            "Marketplace publish failed review_id={} account_id={} marketplace={} status={}",
            review.id,
            account.id,
            account.marketplace.value,
            exc.status_code,
        )
        if exc.status_code == 401:
            await AccountRepository(session).set_active(account.id, False)
        raise
    finally:
        if getattr(client, "_owns_client", False):
            await client.aclose()

    account_user_id = account.user_id
    await consume_api_publish_quota(session, account_user_id)
    await ReviewRepository(session).update_status(review.id, ReviewStatus.PUBLISHED)
    logger.info(
        "Review reply published review_id={} account_id={} marketplace={}",
        review.id,
        account.id,
        account.marketplace.value,
    )
