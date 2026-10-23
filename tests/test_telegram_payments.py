import pytest

from app.core.config import Settings
from app.db.models import PaymentMethod, SubscriptionPlan
from app.services.payment.telegram_stars import (
    invoice_amount,
    invoice_currency,
    invoice_payload,
    invoice_provider_token,
    parse_invoice_payload,
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
    )
    assert uses_telegram_stars(settings) is False
    assert invoice_provider_token(settings) == "2051251535:TEST:abc"
    assert invoice_currency(settings) == "RUB"
    assert invoice_amount(settings, SubscriptionPlan.LITE) == 10000
    assert payment_method_for_invoice(settings) == PaymentMethod.TELEGRAM


def test_without_provider_uses_stars(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PAYMENT_PROVIDER_TOKEN", "")
    settings = Settings(_env_file=None, BOT_TOKEN="x", SUBSCRIPTION_LITE_STARS=100)
    assert uses_telegram_stars(settings) is True
    assert invoice_provider_token(settings) == ""
    assert invoice_currency(settings) == "XTR"
    assert invoice_amount(settings, SubscriptionPlan.LITE) == 100


def test_sub_payload_roundtrip() -> None:
    payload = invoice_payload(SubscriptionPlan.PRO, 99)
    assert payload == "sub:pro:99"
    assert parse_invoice_payload(payload) == (SubscriptionPlan.PRO, 99)
