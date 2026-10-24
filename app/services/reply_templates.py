from __future__ import annotations

import uuid
from typing import Any

from app.db.models import User

MAX_USER_TEMPLATES = 5
MAX_TEMPLATE_LEN = 500


def list_templates(user: User) -> list[dict[str, str]]:
    raw = user.reply_templates or []
    out: list[dict[str, str]] = []
    for item in raw:
        if isinstance(item, dict) and item.get("text"):
            out.append(
                {
                    "id": str(item.get("id") or uuid.uuid4()),
                    "label": str(item.get("label") or "Шаблон")[:24],
                    "text": str(item["text"])[:MAX_TEMPLATE_LEN],
                }
            )
    return out[:MAX_USER_TEMPLATES]


def template_by_id(user: User, template_id: str) -> dict[str, str] | None:
    for item in list_templates(user):
        if item["id"] == template_id:
            return item
    return None


def add_template(user: User, *, label: str, text: str) -> tuple[bool, str | None]:
    items = list_templates(user)
    if len(items) >= MAX_USER_TEMPLATES:
        return False, f"Не больше {MAX_USER_TEMPLATES} шаблонов. Удалите старый."
    clean_text = text.strip()
    if len(clean_text) < 5:
        return False, "Текст шаблона слишком короткий."
    items.append(
        {
            "id": uuid.uuid4().hex[:12],
            "label": label.strip()[:24] or "Шаблон",
            "text": clean_text[:MAX_TEMPLATE_LEN],
        }
    )
    user.reply_templates = items
    return True, None


def remove_template(user: User, template_id: str) -> bool:
    items = [t for t in list_templates(user) if t["id"] != template_id]
    if len(items) == len(list_templates(user)):
        return False
    user.reply_templates = items
    return True


def serialize_for_db(items: list[dict[str, str]]) -> list[Any]:
    return [{"id": i["id"], "label": i["label"], "text": i["text"]} for i in items]
