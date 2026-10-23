from __future__ import annotations

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import encrypt_secret
from app.db.models import Marketplace, MarketplaceAccount
from app.db.repositories.account import AccountRepository
from app.services.marketplace.base import MarketplaceAPIError, MarketplaceReviewDTO
from app.services.marketplace.factory import get_marketplace_client


async def test_and_create_wb_account(
    session: AsyncSession,
    *,
    user_id: int,
    api_key: str,
    shop_name: str | None,
) -> tuple[MarketplaceAccount, MarketplaceReviewDTO | None]:
    encrypted = encrypt_secret(api_key.strip())
    probe = MarketplaceAccount(
        user_id=user_id,
        marketplace=Marketplace.WB,
        encrypted_api_key=encrypted,
        shop_name=shop_name,
        is_active=True,
    )
    client = get_marketplace_client(Marketplace.WB)
    try:
        sample = await client.test_connection(probe)
    except MarketplaceAPIError:
        logger.info("WB connection test failed for user_id={}", user_id)
        raise
    finally:
        if hasattr(client, "aclose"):
            await client.aclose()

    account = await AccountRepository(session).create(
        user_id=user_id,
        marketplace=Marketplace.WB,
        encrypted_api_key=encrypted,
        shop_name=shop_name,
        is_active=True,
    )
    return account, sample


async def test_and_create_ozon_account(
    session: AsyncSession,
    *,
    user_id: int,
    client_id: str,
    api_key: str,
    shop_name: str | None,
) -> tuple[MarketplaceAccount, MarketplaceReviewDTO | None]:
    enc_key = encrypt_secret(api_key.strip())
    enc_client = encrypt_secret(client_id.strip())
    probe = MarketplaceAccount(
        user_id=user_id,
        marketplace=Marketplace.OZON,
        encrypted_api_key=enc_key,
        encrypted_client_id=enc_client,
        shop_name=shop_name,
        is_active=True,
    )
    client = get_marketplace_client(Marketplace.OZON)
    try:
        sample = await client.test_connection(probe)
    except MarketplaceAPIError:
        logger.info("Ozon connection test failed for user_id={}", user_id)
        raise
    finally:
        if hasattr(client, "aclose"):
            await client.aclose()

    account = await AccountRepository(session).create(
        user_id=user_id,
        marketplace=Marketplace.OZON,
        encrypted_api_key=enc_key,
        encrypted_client_id=enc_client,
        shop_name=shop_name,
        is_active=True,
    )
    return account, sample
