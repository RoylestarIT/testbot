from unittest.mock import patch

from app.bot.keyboards.subscription import (
    payment_methods_keyboard,
    subscription_hub_keyboard,
)
from app.services.payment.fx_rates import SubscriptionPricing


def _sample_pricing() -> SubscriptionPricing:
    return SubscriptionPricing(
        lite_rub=800,
        pro_rub=1600,
        lite_byn=30.0,
        pro_byn=60.0,
        source="test",
    )


def test_subscription_hub_compact_layout() -> None:
    kb = subscription_hub_keyboard(_sample_pricing())
    texts = [b.text for row in kb.inline_keyboard for b in row]
    callbacks = [b.callback_data for row in kb.inline_keyboard for b in row]
    assert texts[0] == "💳 Оплатить"
    assert "🧮 Калькулятор" in texts
    assert "📊 Тарифы" in texts
    assert len(kb.inline_keyboard) == 3
    assert "sub:pay:menu" in callbacks
    assert "sub:stars:lite" not in callbacks


def test_payment_methods_lists_crypto_and_card() -> None:
    with patch("app.bot.keyboards.subscription.crypto_pay_enabled", return_value=True):
        kb = payment_methods_keyboard()
    callbacks = [b.callback_data for row in kb.inline_keyboard for b in row]
    assert "sub:pay:crypto" in callbacks
    assert "sub:pay:card" in callbacks
    assert "sub:pay:legal" not in callbacks
