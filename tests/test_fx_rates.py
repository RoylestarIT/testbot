import pytest

from app.services.payment.fx_rates import SubscriptionPricing


def test_format_usd_line() -> None:
    p = SubscriptionPricing(
        lite_usd=10,
        pro_usd=20,
        rub_per_usd=80.0,
        byn_per_usd=3.0,
        source="test",
    )
    assert p.format_usd_line(10) == "$10 ≈ 800 ₽ / 30 BYN"
    assert p.format_usd_line(20) == "$20 ≈ 1 600 ₽ / 60 BYN"
    assert "20" in p.pro_line()
