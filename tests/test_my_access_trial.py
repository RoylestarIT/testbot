import warnings
from datetime import UTC, datetime, timedelta

from app.bot.subscription_ui import build_my_access_text
from app.db.models import User


def _user(trial_until: datetime | None) -> User:
    return User(
        tg_id=1,
        trial_pro_until=trial_until,
        free_api_publishes_remaining=3,
    )


def test_no_trial_is_not_reported_as_active() -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("error", RuntimeWarning)
        text = build_my_access_text(
            _user(None), None, generations_remaining=4, access_tier_line=None
        )
    assert "Trial PRO до" not in text
    assert "Пробных publish осталось" in text
    assert "/ 5" in text


def test_active_trial_is_reported() -> None:
    text = build_my_access_text(
        _user(datetime.now(UTC) + timedelta(days=2)),
        None,
        generations_remaining=None,
        access_tier_line=None,
    )
    assert "Trial PRO до" in text


def test_expired_trial_is_not_reported() -> None:
    text = build_my_access_text(
        _user(datetime.now(UTC) - timedelta(days=1)),
        None,
        generations_remaining=None,
        access_tier_line=None,
    )
    assert "Trial PRO до" not in text
