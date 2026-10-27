"""Daily + hourly checks before LLM generation."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.generation_limit import can_generate
from app.services.plans import has_unlimited_generations
from app.services.user_rate_limit import check_and_record
from app.core.config import get_settings

GENERATION_CALLBACK_PREFIXES = ("review:tone:", "review:more")


def is_generation_callback(callback_data: str) -> bool:
    if callback_data == "review:more":
        return True
    return callback_data.startswith("review:tone:")


async def hourly_generation_limit(session: AsyncSession, user_id: int) -> int:
    settings = get_settings()
    if await has_unlimited_generations(session, user_id):
        return settings.rate_limit_generations_per_hour_paid
    return settings.rate_limit_generations_per_hour_free


async def can_start_generation(session: AsyncSession, user_id: int) -> tuple[bool, str | None]:
    allowed, message = await can_generate(session, user_id)
    if not allowed:
        return False, message
    limit = await hourly_generation_limit(session, user_id)
    return await check_and_record(user_id, "generation", limit=limit)
