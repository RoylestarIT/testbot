from app.services.payment.fx_rates import SubscriptionPricing
from app.services.payment.subscription_calculator import (
    build_calculator_detail,
    build_calculator_table,
)


def test_calculator_table_contains_lite_pro_rub() -> None:
    pricing = SubscriptionPricing(
        lite_usd=10,
        pro_usd=20,
        rub_per_usd=90,
        byn_per_usd=3.3,
        source="test",
    )
    text = build_calculator_table(pricing)
    assert "900" in text
    assert "1 800" in text or "1800" in text
    assert "Калькулятор" in text
    assert "<pre>" not in text
    assert "500</b> отв." in text


def test_calculator_detail_high_volume_favors_subscription() -> None:
    pricing = SubscriptionPricing(
        lite_usd=10,
        pro_usd=20,
        rub_per_usd=90,
        byn_per_usd=3.3,
        source="test",
    )
    text = build_calculator_detail(pricing, 1000)
    assert "1000" in text
    assert "Lite" in text or "PRO" in text
