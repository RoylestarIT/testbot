from __future__ import annotations

from app.services.reply_validation import ReplyValidationError, validate_reply

_VIOLATION_HINTS: dict[str, str] = {
    "contains url": "ссылки запрещены",
    "contains email": "email запрещён",
    "contains phone number": "телефоны запрещены",
    "empty reply": "пустой текст",
}


def validate_reply_for_user(text: str) -> tuple[str | None, str | None]:
    """Возвращает (очищенный текст, сообщение об ошибке для пользователя)."""
    try:
        return validate_reply(text), None
    except ReplyValidationError as exc:
        key = str(exc)
        hint = _VIOLATION_HINTS.get(key)
        if hint is None and key.startswith("forbidden phrase:"):
            hint = "формулировка не подходит для ответа на маркетплейсе"
        if hint is None:
            hint = key
        return None, f"⚠️ Нельзя отправить такой текст: {hint}."
