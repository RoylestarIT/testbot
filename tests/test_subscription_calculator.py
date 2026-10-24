from app.services.payment.fx_rates import SubscriptionPricing
from app.services.payment.subscription_calculator import (
    build_calculator_detail,
    build_calculator_hub,
    build_calculator_table,
)


def test_calculator_table_contains_lite_pro_rub() -> None:
    pricing = SubscriptionPricing(
        lite_rub=800,
        pro_rub=1600,
        lite_byn=30.0,
        pro_byn=60.0,
        source="test",
    )
    text = build_calculator_table(pricing, user_volume=500)
    assert "800" in text
    assert "1 600" in text
    assert "Таблица объёмов" in text
    assert "<pre>" not in text
    assert "500</b> отв" in text
    assert "ваш объём" in text


def test_calculator_hub_compact() -> None:
    pricing = SubscriptionPricing(
        lite_rub=800,
        pro_rub=1600,
        lite_byn=30.0,
        pro_byn=60.0,
        source="test",
    )
    text = build_calculator_hub(pricing, user_volume=200, stars=(1040, 2080))
    assert "Объём" in text
    assert "1040" in text and "⭐" in text
    assert "1000</b> отв" not in text


def test_calculator_detail_high_volume_favors_subscription() -> None:
    pricing = SubscriptionPricing(
        lite_rub=800,
        pro_rub=1600,
        lite_byn=30.0,
        pro_byn=60.0,
        source="test",
    )
    text = build_calculator_detail(pricing, 1000, stars=(1040, 2080))
    assert "1000" in text
    assert "Lite" in text or "PRO" in text
    assert "Почему подписка" in text
    assert "Telegram" in text
    assert "15–25" in text
    assert "1040" in text


def test_calculator_detail_low_volume_honest() -> None:
    pricing = SubscriptionPricing(
        lite_rub=800,
        pro_rub=1600,
        lite_byn=30.0,
        pro_byn=60.0,
        source="test",
    )
    text = build_calculator_detail(pricing, 100)
    assert "Небольшой объём" in text
    assert "честные" in text
