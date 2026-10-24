from app.bot.subscription_ui import build_subscription_hub
from app.services.payment.fx_rates import SubscriptionPricing


def test_hub_is_short_and_structured() -> None:
    pricing = SubscriptionPricing(
        lite_usd=10,
        pro_usd=20,
        rub_per_usd=90,
        byn_per_usd=3.3,
        source="test",
    )
    text = build_subscription_hub(pricing, access_line="Free")
    assert "Подписка" in text
    assert "Lite" in text
    assert "PRO" in text
    assert "Почему мы" not in text
    assert text.count("───────────────") == 1
    assert len(text) < 450
