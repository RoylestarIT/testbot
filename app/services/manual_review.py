import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import EncryptionError, encrypt_secret
from app.db.models import Marketplace, MarketplaceAccount
from app.constants import MANUAL_SHOP_NAME
from app.db.repositories.account import AccountRepository


def _manual_api_key_ciphertext() -> str:
    try:
        return encrypt_secret("manual-input")
    except EncryptionError:
        return "manual-input-unencrypted"


async def get_or_create_manual_account(session: AsyncSession, user_id: int) -> MarketplaceAccount:
    repo = AccountRepository(session)
    for account in await repo.list_by_user_id(user_id):
        if account.shop_name == MANUAL_SHOP_NAME:
            return account
    return await repo.create(
        user_id=user_id,
        marketplace=Marketplace.WB,
        encrypted_api_key=_manual_api_key_ciphertext(),
        shop_name=MANUAL_SHOP_NAME,
        is_active=True,
    )


def new_manual_external_id() -> str:
    return f"manual-{uuid.uuid4().hex}"
