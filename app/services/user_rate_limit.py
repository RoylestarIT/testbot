"""In-memory sliding-window rate limits per user (single bot process)."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta

from app.core.config import Settings, get_settings

_lock = asyncio.Lock()
_events: dict[tuple[int, str], list[datetime]] = {}


def _window_for(action: str) -> timedelta:
    return timedelta(hours=1)


def default_limit_for(action: str, settings: Settings) -> int:
    if action == "sync":
        return settings.rate_limit_sync_per_hour
    if action == "support":
        return settings.rate_limit_support_per_hour
    return settings.rate_limit_generations_per_hour_free


def _prune(times: list[datetime], window: timedelta) -> list[datetime]:
    cutoff = datetime.now(UTC) - window
    return [t for t in times if t >= cutoff]


def minutes_until_oldest_expires(times: list[datetime], window: timedelta) -> int:
    if not times:
        return 1
    oldest = min(times)
    reset_at = oldest + window
    seconds = (reset_at - datetime.now(UTC)).total_seconds()
    return max(1, int(seconds // 60) + (1 if seconds % 60 else 0))


async def check_and_record(
    user_id: int,
    action: str,
    *,
    limit: int | None = None,
    settings: Settings | None = None,
    deny_message: str | None = None,
) -> tuple[bool, str | None]:
    """Returns (allowed, user_message_if_denied). Records event when allowed."""
    settings = settings or get_settings()
    window = _window_for(action)
    effective_limit = limit if limit is not None else default_limit_for(action, settings)
    key = (user_id, action)
    async with _lock:
        times = _prune(_events.get(key, []), window)
        if len(times) >= effective_limit:
            wait = minutes_until_oldest_expires(times, window)
            if deny_message:
                msg = deny_message
            elif action == "sync":
                msg = (
                    f"Обновление отзывов — не чаще {effective_limit} раз в час. "
                    f"Подождите около {wait} мин."
                )
            elif action == "support":
                msg = (
                    f"Сообщений в поддержку — не больше {effective_limit} в час. "
                    f"Подождите около {wait} мин."
                )
            elif action == "generation":
                msg = (
                    f"Подготовка ответов — не больше {effective_limit} в час. "
                    f"Подождите около {wait} мин."
                )
            else:
                msg = f"Слишком частые действия. Подождите около {wait} мин."
            return False, msg
        times.append(datetime.now(UTC))
        _events[key] = times
    return True, None


def reset_all_for_tests() -> None:
    _events.clear()
