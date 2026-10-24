from __future__ import annotations

from datetime import UTC, datetime

from app.db.models import User


def user_should_see_trial_ended_banner(user: User) -> bool:
    if not user.trial_pro_used or user.trial_pro_until is None:
        return False
    until = user.trial_pro_until
    if until.tzinfo is None:
        until = until.replace(tzinfo=UTC)
    if until > datetime.now(UTC):
        return False
    return user.trial_ended_ack_at is None
