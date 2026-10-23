from app.db.models import Marketplace, MarketplaceAccount
from app.services.marketplace.base import MarketplaceClient
from app.services.marketplace.ozon import OzonClient
from app.services.marketplace.wildberries import WildberriesClient


def get_marketplace_client(marketplace: Marketplace) -> MarketplaceClient:
    if marketplace == Marketplace.OZON:
        return OzonClient()
    return WildberriesClient()


def get_client_for_account(account: MarketplaceAccount) -> MarketplaceClient:
    return get_marketplace_client(account.marketplace)
