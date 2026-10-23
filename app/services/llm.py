from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

from loguru import logger
from openai import AsyncOpenAI

from app.core.config import Settings, get_settings
from app.services.reply_validation import find_reply_violation, is_valid_reply


class LLMError(RuntimeError):
    """LLM request or response processing failed."""


@dataclass(slots=True)
class ToneProfileInput:
    description: str | None = None
    example_replies: list[str] | None = None


def _build_client(settings: Settings) -> AsyncOpenAI:
    if not settings.openai_api_key.strip():
        raise LLMError("OPENAI_API_KEY is not configured")
    return AsyncOpenAI(
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
    )


def _rating_guidance(rating: int | None) -> str:
    if rating is not None and rating <= 3:
        return (
            "Отзыв негативный (1–3 звезды): проявите эмпатию, признайте проблему, "
            "предложите конкретное решение (замена, возврат через кабинет маркетплейса, "
            "уточнение деталей). Без обещаний, которых нельзя выполнить, без давления."
        )
    if rating is not None and rating >= 4:
        return (
            "Отзыв позитивный (4–5 звёзд): поблагодарите покупателя, отметьте деталь из отзыва, "
            "добавьте лёгкий CTA (будем рады снова видеть вас / загляните в новинки) без ссылок и контактов."
        )
    return (
        "Рейтинг не указан: нейтральный вежливый ответ, без ссылок и контактов."
    )


def _format_tone_profile(tone_profile: ToneProfileInput | None) -> str:
    if tone_profile is None:
        return "Тон: дружелюбный, профессиональный, лаконичный (по умолчанию)."
    parts: list[str] = []
    if tone_profile.description:
        parts.append(f"Описание тона: {tone_profile.description.strip()}")
    if tone_profile.example_replies:
        examples = "\n".join(f"- {item}" for item in tone_profile.example_replies[:5])
        parts.append(f"Примеры ответов магазина:\n{examples}")
    if not parts:
        return "Тон: дружелюбный, профессиональный, лаконичный (по умолчанию)."
    return "\n".join(parts)


def build_prompt(
    review_text: str,
    rating: int | None,
    tone_profile: ToneProfileInput | None,
    count: int,
) -> tuple[str, str]:
    system = (
        "Ты — опытный менеджер маркетплейса (Wildberries/Ozon). "
        "Пишешь ответы продавца на отзывы покупателей от имени магазина. "
        "Строго запрещено: URL, email, телефоны, мессенджеры, призывы писать в личку, реклама сторонних сервисов. "
        "Не обещай рост рейтинга и нереалистичные компенсации. "
        f"Верни ровно JSON без markdown: {{\"replies\": [\"...\", ...]}} — {count} различных варианта на русском."
    )
    user = (
        f"{_format_tone_profile(tone_profile)}\n\n"
        f"{_rating_guidance(rating)}\n\n"
        f"Рейтинг: {rating if rating is not None else 'не указан'}\n"
        f"Текст отзыва:\n{review_text.strip()}\n\n"
        f"Сгенерируй {count} варианта ответа."
    )
    return system, user


def parse_replies_json(raw_content: str, *, expected_count: int | None = None) -> list[str]:
    content = raw_content.strip()
    if not content:
        raise LLMError("Empty LLM response")

    candidates: list[Any] = []

    try:
        candidates.append(json.loads(content))
    except json.JSONDecodeError:
        pass

    fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", content, re.IGNORECASE)
    if fence_match:
        try:
            candidates.append(json.loads(fence_match.group(1).strip()))
        except json.JSONDecodeError:
            pass

    object_match = re.search(r"\{[\s\S]*\}", content)
    if object_match:
        try:
            candidates.append(json.loads(object_match.group(0)))
        except json.JSONDecodeError:
            pass

    array_match = re.search(r"\[[\s\S]*\]", content)
    if array_match:
        try:
            candidates.append(json.loads(array_match.group(0)))
        except json.JSONDecodeError:
            pass

    replies: list[str] = []
    for parsed in candidates:
        replies = _extract_reply_strings(parsed)
        if replies:
            break

    if not replies:
        replies = [line.strip() for line in content.splitlines() if line.strip()]

    if expected_count is not None and len(replies) > expected_count:
        replies = replies[:expected_count]

    if not replies:
        raise LLMError("Could not parse replies from LLM response")

    return replies


def _extract_reply_strings(parsed: Any) -> list[str]:
    if isinstance(parsed, dict):
        for key in ("replies", "variants", "answers", "responses"):
            value = parsed.get(key)
            if isinstance(value, list):
                return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(parsed, list):
        return [str(item).strip() for item in parsed if str(item).strip()]
    return []


def filter_valid_replies(replies: list[str]) -> list[str]:
    valid: list[str] = []
    for reply in replies:
        violation = find_reply_violation(reply)
        if violation is None:
            valid.append(reply.strip())
        else:
            logger.warning("Rejected LLM reply variant: {}", violation)
    return valid


async def generate_replies(
    review_text: str,
    rating: int | None,
    tone_profile: ToneProfileInput | None,
    count: int = 3,
    *,
    client: AsyncOpenAI | None = None,
    settings: Settings | None = None,
) -> list[str]:
    if count < 1:
        raise ValueError("count must be at least 1")
    if not review_text.strip():
        raise ValueError("review_text must not be empty")

    cfg = settings or get_settings()
    llm_client = client or _build_client(cfg)
    system, user = build_prompt(review_text, rating, tone_profile, count)

    try:
        response = await llm_client.chat.completions.create(
            model=cfg.openai_model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
        )
    except Exception as exc:
        raise LLMError("LLM request failed") from exc

    message = response.choices[0].message.content if response.choices else None
    if not message:
        raise LLMError("LLM returned empty message")

    raw_replies = parse_replies_json(message, expected_count=count)
    valid_replies = filter_valid_replies(raw_replies)

    if not valid_replies:
        raise LLMError("All LLM reply variants failed validation")

    return valid_replies[:count]
