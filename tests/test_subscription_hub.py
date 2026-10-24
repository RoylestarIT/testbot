import pytest

from app.bot.handlers.subscription import _subscription_hub_text
from app.db.models import User
from app.services.payment.fx_rates import SubscriptionPricing


@pytest.mark.asyncio
async def test_subscription_hub_text_new_user_no_name_error() -> None:
    user = User(id=1, tg_id=999001, username="newbie")
    pricing = SubscriptionPricing(
        lite_usd=10.0,
        pro_usd=20.0,
        rub_per_usd=90.0,
        byn_per_usd=3.3,
        source="test",
    )
    text = await _subscription_hub_text(user, pricing)
    assert "Подписка" in text or "Lite" in text or "💎" in text
