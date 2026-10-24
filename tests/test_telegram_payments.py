import pytest

from app.core.config import Settings
from app.db.models import PaymentMethod, SubscriptionPlan
from app.services.payment.payment_options import card_payments_enabled, stars_payments_enabled
from app.services.payment.telegram_stars import (
    invoice_amount,
    invoice_currency,
    invoice_payload,
    invoice_provider_token,
    parse_invoice_payload,
    payment_method_for_currency,
    payment_method_for_invoice,
    uses_telegram_stars,
)


def test_parse_legacy_stars_payload() -> None:
    assert parse_invoice_payload("stars:lite:7") == (SubscriptionPlan.LITE, 7)


def test_provider_token_enables_fiat_invoices() -> None:
    settings = Settings(
        _env_file=None,
        BOT_TOKEN="x",
        PAYMENT_PROVIDER_TOKEN="2051251535:TEST:abc",
        PAYMENT_CURRENCY="RUB",
        SUBSCRIPTION_LITE_PRICE_MINOR=10000,
        SUBSCRIPTION_PRO_PRICE_MINOR=30000,
        PAYMENT_ENABLE_STARS=True,
    )
    assert uses_telegram_stars(settings) is False
    assert card_payments_enabled(settings) is True
    assert stars_payments_enabled(settings) is True
    assert invoice_provider_token(for_stars=False, settings=settings) == "2051251535:TEST:abc"
    assert invoice_currency(for_stars=False, settings=settings) == "RUB"
    assert invoice_amount(settings, SubscriptionPlan.LITE, for_stars=False) == 10000
    assert invoice_amount(settings, SubscriptionPlan.LITE, for_stars=True) == 750
    assert payment_method_for_invoice(settings, for_stars=False) == PaymentMethod.TELEGRAM
    assert payment_method_for_currency("XTR") == PaymentMethod.STARS


def test_stars_only_without_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PAYMENT_PROVIDER_TOKEN", "")
    settings = Settings(
        _env_file=None,
        BOT_TOKEN="x",
        SUBSCRIPTION_LITE_STARS=100,
        PAYMENT_ENABLE_STARS=True,
    )
    assert uses_telegram_stars(settings) is True
    assert stars_payments_enabled(settings) is True
    assert card_payments_enabled(settings) is False
    assert invoice_provider_token(for_stars=True) == ""
    assert invoice_currency(for_stars=True) == "XTR"
    assert invoice_amount(settings, SubscriptionPlan.LITE, for_stars=True) == 100


def test_sub_payload_roundtrip() -> None:
    payload = invoice_payload(SubscriptionPlan.PRO, 99)
    assert payload == "sub:pro:99"
    assert parse_invoice_payload(payload) == (SubscriptionPlan.PRO, 99)
