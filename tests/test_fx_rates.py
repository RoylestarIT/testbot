from app.services.payment.fx_rates import SubscriptionPricing


def test_fixed_price_labels() -> None:
    p = SubscriptionPricing(lite_rub=800, pro_rub=1600, lite_byn=30.0, pro_byn=60.0, source="test")
    assert p.lite_price_label() == "800 ₽ / 30 BYN"
    assert p.pro_price_label() == "1 600 ₽ / 60 BYN"
    assert "800" in p.lite_line()
    assert "1 600" in p.pro_line()
