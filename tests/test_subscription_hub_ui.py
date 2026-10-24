from app.bot.subscription_ui import build_subscription_hub
from app.services.payment.fx_rates import SubscriptionPricing


def test_hub_is_short_and_structured() -> None:
    pricing = SubscriptionPricing(
        lite_rub=800,
        pro_rub=1600,
        lite_byn=30.0,
        pro_byn=60.0,
        source="test",
    )
    text = build_subscription_hub(pricing, access_line="Free")
    assert "Подписка" in text
    assert "800" in text
    assert "Lite" in text
    assert "PRO" in text
    assert "Почему мы" not in text
    assert "промокод" not in text.lower()
    assert text.count("───────────────") == 1
    assert len(text) < 450
