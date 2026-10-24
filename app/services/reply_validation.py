import re

URL_PATTERN = re.compile(
    r"(https?://|www\.)[^\s]+",
    re.IGNORECASE,
)
EMAIL_PATTERN = re.compile(
    r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
)
PHONE_PATTERN = re.compile(
    r"(?<!\d)(?:\+?\d{1,3}[\s\-().]*)?(?:\(?\d{2,4}\)?[\s\-.]*)?\d{3}[\s\-.]?\d{2}[\s\-.]?\d{2}(?:[\s\-.]?\d{2})?(?!\d)",
)

FORBIDDEN_PHRASES: tuple[str, ...] = (
    "whatsapp",
    "viber",
    "telegram",
    "телеграм",
    "в личку",
    "личные сообщения",
    "напишите в директ",
    "пишите в директ",
    "по ссылке",
    "перейдите по",
    "скидка только",
    "гарантируем 100",
    "вернём деньги",
    "компенсируем",
    "суд",
    "роспотребнадзор",
)


class ReplyValidationError(ValueError):
    """Reply text failed content policy checks."""


def find_reply_violation(text: str) -> str | None:
    normalized = text.strip()
    if not normalized:
        return "empty reply"

    if URL_PATTERN.search(normalized):
        return "contains url"

    if EMAIL_PATTERN.search(normalized):
        return "contains email"

    if PHONE_PATTERN.search(normalized):
        return "contains phone number"

    lowered = normalized.lower()
    for phrase in FORBIDDEN_PHRASES:
        if phrase in lowered:
            return f"forbidden phrase: {phrase}"

    return None


def is_valid_reply(text: str) -> bool:
    return find_reply_violation(text) is None


def validate_reply(text: str) -> str:
    violation = find_reply_violation(text)
    if violation is not None:
        raise ReplyValidationError(violation)
    return text.strip()
