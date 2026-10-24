"""In-process Telegram update activity (since last bot restart)."""

from __future__ import annotations

from datetime import UTC, datetime

from app.tasks.poller import format_ui_time

_started_at: datetime = datetime.now(UTC)
_last_update_at: datetime | None = None
_updates_total: int = 0


def record_update() -> None:
    global _last_update_at, _updates_total
    _last_update_at = datetime.now(UTC)
    _updates_total += 1


def activity_snapshot() -> dict[str, object]:
    return {
        "started_at": _started_at.isoformat(),
        "last_update_at": _last_update_at.isoformat() if _last_update_at else None,
        "last_update_minsk": format_ui_time(_last_update_at) if _last_update_at else None,
        "updates_since_boot": _updates_total,
    }
