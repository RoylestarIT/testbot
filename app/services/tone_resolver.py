from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.tone_profile import ToneProfileRepository
from app.services.llm import ToneProfileInput


def _examples_from_json(raw: Any) -> list[str] | None:
    if not raw:
        return None
    if isinstance(raw, list):
        return [str(item) for item in raw]
    return None


_TONE_PRESETS: dict[str, ToneProfileInput] = {
    "preset:grateful": ToneProfileInput(
        description="Тёплая благодарность, без оправданий, 2–3 предложения.",
        example_replies=["Спасибо за отзыв! Рады, что покупка оправдала ожидания."],
    ),
    "preset:apology": ToneProfileInput(
        description="Извинение за неудобства, предложение помощи, без агрессии.",
        example_replies=["Жаль, что так вышло. Напишите нам в поддержку — разберёмся."],
    ),
    "preset:neutral": ToneProfileInput(
        description="Спокойный деловой тон, факты, без эмоций.",
    ),
}


async def resolve_tone_input(session: AsyncSession, user_id: int, tone_key: str) -> ToneProfileInput:
    if tone_key in _TONE_PRESETS:
        return _TONE_PRESETS[tone_key]
    if tone_key == "default":
        profiles = await ToneProfileRepository(session).list_by_user_id(user_id)
        for profile in profiles:
            if profile.is_default and profile.description:
                return ToneProfileInput(
                    description=profile.description,
                    example_replies=_examples_from_json(profile.example_replies),
                )
        return ToneProfileInput(description="Дружелюбный, профессиональный, лаконичный")

    profile = await ToneProfileRepository(session).get_by_id(int(tone_key))
    if profile is None or profile.user_id != user_id:
        return ToneProfileInput(description="Дружелюбный, профессиональный, лаконичный")
    return ToneProfileInput(
        description=profile.description or "Дружелюбный, профессиональный, лаконичный",
        example_replies=_examples_from_json(profile.example_replies),
    )
