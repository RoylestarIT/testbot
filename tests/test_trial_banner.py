from datetime import UTC, datetime, timedelta

from app.db.models import User
from app.services.trial_banner import user_should_see_trial_ended_banner


def test_trial_ended_banner_when_expired_and_not_acked() -> None:
    user = User(
        id=1,
        tg_id=1,
        trial_pro_used=True,
        trial_pro_until=datetime.now(UTC) - timedelta(days=1),
    )
    assert user_should_see_trial_ended_banner(user) is True


def test_no_banner_when_acked() -> None:
    user = User(
        id=1,
        tg_id=1,
        trial_pro_used=True,
        trial_pro_until=datetime.now(UTC) - timedelta(days=1),
        trial_ended_ack_at=datetime.now(UTC),
    )
    assert user_should_see_trial_ended_banner(user) is False
