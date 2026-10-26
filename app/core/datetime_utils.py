from __future__ import annotations

from datetime import UTC, datetime


def as_utc(dt: datetime | None) -> datetime | None:
    """Normalize DB datetimes (SQLite often returns naive UTC) for comparisons."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)
