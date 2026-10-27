from datetime import UTC, datetime, timedelta

from app.core.config import Settings
from app.db.models import Subscription, SubscriptionPlan, SubscriptionStatus, User
from app.services.access_messaging import trial_pro_activated_text


def test_trial_activated_text_explains_after_trial() -> None:
    user = User(
        id=1,
        tg_id=1,
        trial_pro_used=True,
        trial_pro_until=datetime.now(UTC) + timedelta(days=3),
        free_api_publishes_remaining=3,
    )
    text = trial_pro_activated_text(user, Settings())
    assert "Пробный PRO" in text
    assert "После окончания" in text
    assert "не тратятся" in text
