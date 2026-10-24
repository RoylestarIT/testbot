import pytest

from app.bot.handlers.subscription import _subscription_hub_text
from app.db.models import User
from app.services.payment.fx_rates import SubscriptionPricing


@pytest.mark.asyncio
async def test_subscription_hub_text_new_user_no_name_error() -> None:
    user = User(id=1, tg_id=999001, username="newbie")
    pricing = SubscriptionPricing(
        lite_rub=800,
        pro_rub=1600,
        lite_byn=30.0,
        pro_byn=60.0,
        source="test",
    )
    text = await _subscription_hub_text(user, pricing)
    assert "800" in text
    assert "1 600" in text
    assert "промокод" not in text.lower()
