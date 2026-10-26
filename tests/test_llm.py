import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.config import Settings, get_settings
from app.services.llm import (
    LLMError,
    ToneProfileInput,
    build_prompt,
    filter_valid_replies,
    generate_replies,
    parse_replies_json,
)


def test_build_prompt_includes_negative_guidance_for_low_rating() -> None:
    _, user = build_prompt("Товар бракованный", 2, None, 3)
    assert "негативный" in user.lower() or "1–3" in user


def test_build_prompt_includes_tone_description() -> None:
    tone = ToneProfileInput(description="Кратко и по делу", example_replies=["Спасибо!"])
    _, user = build_prompt("Отлично", 5, tone, 2)
    assert "Кратко и по делу" in user
    assert "Спасибо!" in user


def test_build_prompt_includes_product_context() -> None:
    _, user = build_prompt(
        "Размер не подошёл",
        3,
        None,
        2,
        product_context="Название: Куртка; Артикул WB: 42",
    )
    assert "Товар:" in user
    assert "Куртка" in user
    assert "42" in user


def test_parse_replies_json_plain_object() -> None:
    raw = json.dumps({"replies": ["A", "B", "C"]}, ensure_ascii=False)
    assert parse_replies_json(raw) == ["A", "B", "C"]


def test_parse_replies_json_markdown_fence_fallback() -> None:
    raw = 'Вот ответ:\n```json\n{"replies": ["X", "Y"]}\n```'
    assert parse_replies_json(raw) == ["X", "Y"]


def test_parse_replies_json_array_fallback() -> None:
    raw = 'noise ["first", "second"]'
    assert parse_replies_json(raw) == ["first", "second"]


def test_filter_valid_replies_drops_invalid() -> None:
    replies = [
        "Спасибо за покупку!",
        "Пишите в telegram",
        "Будем рады снова!",
    ]
    assert filter_valid_replies(replies) == [
        "Спасибо за покупку!",
        "Будем рады снова!",
    ]


def _make_mock_client(content: str) -> AsyncMock:
    message = MagicMock()
    message.content = content
    choice = MagicMock()
    choice.message = message
    response = MagicMock()
    response.choices = [choice]

    client = AsyncMock()
    client.chat.completions.create = AsyncMock(return_value=response)
    return client


@pytest.mark.asyncio
async def test_generate_replies_with_mock_client() -> None:
    payload = {
        "replies": [
            "Спасибо за отзыв! Рады, что всё понравилось.",
            "Благодарим за покупку — возвращайтесь за новинками.",
            "Очень приятно читать такие отзывы. Хорошего дня!",
        ]
    }
    client = _make_mock_client(json.dumps(payload, ensure_ascii=False))
    settings = Settings(
        BOT_TOKEN="test",
        OPENAI_API_KEY="sk-test",
        OPENAI_BASE_URL="https://api.example.com/v1",
        OPENAI_MODEL="test-model",
    )

    replies = await generate_replies(
        "Отличный товар",
        5,
        ToneProfileInput(description="Тёплый тон"),
        count=3,
        client=client,
        settings=settings,
    )

    assert len(replies) == 3
    call_kwargs = client.chat.completions.create.await_args.kwargs
    assert call_kwargs["model"] == "test-model"
    assert call_kwargs["response_format"] == {"type": "json_object"}


@pytest.mark.asyncio
async def test_generate_replies_filters_invalid_variants() -> None:
    payload = {
        "replies": [
            "Спасибо за отзыв!",
            "Пишите нам в whatsapp",
            "Будем рады снова!",
        ]
    }
    client = _make_mock_client(json.dumps(payload, ensure_ascii=False))
    settings = Settings(
        BOT_TOKEN="test",
        OPENAI_API_KEY="sk-test",
        OPENAI_BASE_URL="https://api.example.com/v1",
        OPENAI_MODEL="test-model",
    )

    replies = await generate_replies(
        "Нормально",
        4,
        None,
        count=3,
        client=client,
        settings=settings,
    )
    assert replies == ["Спасибо за отзыв!", "Будем рады снова!"]


@pytest.mark.asyncio
async def test_generate_replies_raises_when_all_invalid() -> None:
    payload = {"replies": ["Пишите в telegram", "https://bad.link"]}
    client = _make_mock_client(json.dumps(payload))
    settings = Settings(
        BOT_TOKEN="test",
        OPENAI_API_KEY="sk-test",
        OPENAI_BASE_URL="https://api.example.com/v1",
        OPENAI_MODEL="test-model",
    )

    with pytest.raises(LLMError):
        await generate_replies("Плохо", 1, None, client=client, settings=settings)

    get_settings.cache_clear()
