from app.core.config import Settings, get_settings
from app.services.payment.crypto_pay import crypto_pay_enabled
from app.services.payment.telegram_stars import fiat_invoices_configured, stars_invoices_configured


def card_payments_enabled(settings: Settings | None = None) -> bool:
    settings = settings or get_settings()
    return fiat_invoices_configured(settings)


def stars_payments_enabled(settings: Settings | None = None) -> bool:
    settings = settings or get_settings()
    return stars_invoices_configured(settings)


def transfer_payments_enabled(settings: Settings | None = None) -> bool:
    return True
