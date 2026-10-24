import pytest

from app.services.reply_validation import (
    ReplyValidationError,
    find_reply_violation,
    is_valid_reply,
    validate_reply,
)


@pytest.mark.parametrize(
    ("text", "reason_part"),
    [
        ("Спасибо! Подробности на https://shop.example", "url"),
        ("Пишите на help@shop.ru", "email"),
        ("Звоните +7 999 123-45-67", "phone"),
        ("Напишите нам в telegram", "forbidden"),
        ("", "empty"),
    ],
)
def test_find_reply_violation_detects_issues(text: str, reason_part: str) -> None:
    violation = find_reply_violation(text)
    assert violation is not None
    assert reason_part in violation


def test_is_valid_reply_accepts_clean_text() -> None:
    text = (
        "Спасибо за отзыв! Нам приятно, что товар оправдал ожидания. "
        "Будем рады видеть вас снова среди наших покупателей."
    )
    assert is_valid_reply(text) is True
    assert validate_reply(text) == text


def test_validate_reply_raises_for_url() -> None:
    with pytest.raises(ReplyValidationError):
        validate_reply("Смотрите www.example.com")
