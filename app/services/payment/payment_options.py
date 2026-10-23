from app.core.config import Settings, get_settings
from app.services.payment.crypto_pay import crypto_pay_enabled
from app.services.payment.telegram_stars import uses_telegram_stars


def card_payments_enabled(settings: Settings | None = None) -> bool:
    settings = settings or get_settings()
    return bool(settings.payment_provider_token.strip())


def stars_payments_enabled(settings: Settings | None = None) -> bool:
    settings = settings or get_settings()
    return uses_telegram_stars(settings) and settings.payment_enable_stars


def transfer_payments_enabled(settings: Settings | None = None) -> bool:
    return True
