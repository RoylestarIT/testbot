from app.db.models import Marketplace, MarketplaceAccount
from app.services.marketplace.base import MarketplaceClient
from app.services.marketplace.http_pool import get_ozon_http_client, get_wb_http_client
from app.services.marketplace.ozon import OzonClient
from app.services.marketplace.wildberries import WildberriesClient


def get_marketplace_client(marketplace: Marketplace, *, use_shared_http: bool = True) -> MarketplaceClient:
    if marketplace == Marketplace.OZON:
        if use_shared_http:
            return OzonClient(http_client=get_ozon_http_client())
        return OzonClient()
    if use_shared_http:
        return WildberriesClient(http_client=get_wb_http_client())
    return WildberriesClient()


def get_client_for_account(account: MarketplaceAccount) -> MarketplaceClient:
    return get_marketplace_client(account.marketplace)
