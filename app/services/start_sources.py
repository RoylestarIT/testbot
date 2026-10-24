from __future__ import annotations

from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User

ALLOWED_SOURCES = frozenset({"site", "health", "organic", "promo", "unknown"})


def normalize_start_payload(raw: str | None) -> str:
    if not raw:
        return "organic"
    key = raw.strip().lower()[:32]
    if not key.replace("_", "").isalnum():
        return "unknown"
    return key if key in ALLOWED_SOURCES or len(key) <= 24 else key[:24]


def increment_start_source(user: User, source: str) -> None:
    source = normalize_start_payload(source)
    data: dict[str, int] = {}
    if isinstance(user.start_source_counts, dict):
        data = {str(k): int(v) for k, v in user.start_source_counts.items()}
    data[source] = data.get(source, 0) + 1
    user.start_source_counts = data


async def aggregate_start_sources(session: AsyncSession, *, limit: int = 12) -> list[tuple[str, int]]:
    result = await session.execute(select(User.start_source_counts))
    totals: dict[str, int] = defaultdict(int)
    for (counts,) in result.all():
        if not isinstance(counts, dict):
            continue
        for key, val in counts.items():
            try:
                totals[str(key)] += int(val)
            except (TypeError, ValueError):
                continue
    ranked = sorted(totals.items(), key=lambda x: (-x[1], x[0]))
    return ranked[:limit]
