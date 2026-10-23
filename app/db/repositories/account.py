from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Marketplace, MarketplaceAccount
from app.constants import MANUAL_SHOP_NAME


class AccountRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, account_id: int) -> MarketplaceAccount | None:
        return await self._session.get(MarketplaceAccount, account_id)

    async def list_by_user_id(self, user_id: int, *, active_only: bool = False) -> list[MarketplaceAccount]:
        stmt = select(MarketplaceAccount).where(MarketplaceAccount.user_id == user_id)
        if active_only:
            stmt = stmt.where(MarketplaceAccount.is_active.is_(True))
        result = await self._session.execute(stmt.order_by(MarketplaceAccount.id))
        return list(result.scalars().all())

    async def create(
        self,
        *,
        user_id: int,
        marketplace: Marketplace,
        encrypted_api_key: str,
        encrypted_client_id: str | None = None,
        shop_name: str | None = None,
        is_active: bool = True,
    ) -> MarketplaceAccount:
        account = MarketplaceAccount(
            user_id=user_id,
            marketplace=marketplace,
            encrypted_api_key=encrypted_api_key,
            encrypted_client_id=encrypted_client_id,
            shop_name=shop_name,
            is_active=is_active,
        )
        self._session.add(account)
        await self._session.flush()
        await self._session.refresh(account)
        return account

    async def list_active_all(self) -> list[MarketplaceAccount]:
        stmt = select(MarketplaceAccount).where(MarketplaceAccount.is_active.is_(True))
        result = await self._session.execute(stmt.order_by(MarketplaceAccount.id))
        return list(result.scalars().all())

    async def list_active_for_api_sync(self) -> list[MarketplaceAccount]:
        """Активные кабинеты с реальным Seller API (без «Ручной ввод»)."""
        stmt = select(MarketplaceAccount).where(
            MarketplaceAccount.is_active.is_(True),
            MarketplaceAccount.marketplace.in_((Marketplace.WB, Marketplace.OZON)),
            (MarketplaceAccount.shop_name.is_(None))
            | (MarketplaceAccount.shop_name != MANUAL_SHOP_NAME),
        )
        result = await self._session.execute(stmt.order_by(MarketplaceAccount.id))
        return list(result.scalars().all())

    async def set_active(self, account_id: int, is_active: bool) -> MarketplaceAccount | None:
        account = await self.get_by_id(account_id)
        if account is None:
            return None
        account.is_active = is_active
        await self._session.flush()
        return account

    async def set_auto_publish(self, account_id: int, enabled: bool) -> MarketplaceAccount | None:
        account = await self.get_by_id(account_id)
        if account is None:
            return None
        account.auto_publish_enabled = enabled
        await self._session.flush()
        return account

    async def update_wb_api_key(self, account_id: int, encrypted_api_key: str) -> MarketplaceAccount | None:
        account = await self.get_by_id(account_id)
        if account is None or account.marketplace != Marketplace.WB:
            return None
        account.encrypted_api_key = encrypted_api_key
        account.is_active = True
        account.last_sync_error = None
        await self._session.flush()
        return account

    async def update_ozon_credentials(
        self,
        account_id: int,
        *,
        encrypted_api_key: str,
        encrypted_client_id: str,
    ) -> MarketplaceAccount | None:
        account = await self.get_by_id(account_id)
        if account is None or account.marketplace != Marketplace.OZON:
            return None
        account.encrypted_api_key = encrypted_api_key
        account.encrypted_client_id = encrypted_client_id
        account.is_active = True
        account.last_sync_error = None
        await self._session.flush()
        return account
