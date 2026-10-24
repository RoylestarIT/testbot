"""Очередь вопросов WB: список и snooze (без авто-ответа)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from app.db.models import MarketplaceAccount, User

SNOOZE_HOURS = 24
SNOOZE_KEY_SEP = ":"


def _snooze_key(account_id: int, question_id: str) -> str:
    return f"{account_id}{SNOOZE_KEY_SEP}{question_id}"


def parse_snooze_key(key: str) -> tuple[int, str] | None:
    if SNOOZE_KEY_SEP not in key:
        return None
    acc_s, qid = key.split(SNOOZE_KEY_SEP, 1)
    try:
        return int(acc_s), qid
    except ValueError:
        return None


def _snooze_map(user: User) -> dict[str, str]:
    raw = user.wb_question_snoozes
    if not isinstance(raw, dict):
        return {}
    return {str(k): str(v) for k, v in raw.items()}


def prune_expired_snoozes(user: User) -> bool:
    now = datetime.now(UTC)
    data = _snooze_map(user)
    changed = False
    for key, iso in list(data.items()):
        try:
            until = datetime.fromisoformat(iso.replace("Z", "+00:00"))
            if until.tzinfo is None:
                until = until.replace(tzinfo=UTC)
        except ValueError:
            del data[key]
            changed = True
            continue
        if until <= now:
            del data[key]
            changed = True
    if changed:
        user.wb_question_snoozes = data
    return changed


def is_question_snoozed(user: User, account_id: int, question_id: str) -> bool:
    prune_expired_snoozes(user)
    key = _snooze_key(account_id, question_id)
    return key in _snooze_map(user)


def snooze_question(user: User, account_id: int, question_id: str, *, hours: int = SNOOZE_HOURS) -> None:
    until = datetime.now(UTC) + timedelta(hours=hours)
    data = _snooze_map(user)
    data[_snooze_key(account_id, question_id)] = until.isoformat()
    user.wb_question_snoozes = data


def filter_visible_questions(
    user: User,
    account: MarketplaceAccount,
    items: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    prune_expired_snoozes(user)
    out: list[dict[str, Any]] = []
    for item in items:
        qid = str(item.get("id") or "")
        if not qid or is_question_snoozed(user, account.id, qid):
            continue
        out.append(item)
    return out


def question_id_from_item(item: dict[str, Any]) -> str:
    return str(item.get("id") or "")


def format_question_preview(item: dict[str, Any], *, max_len: int = 100) -> str:
    text = (item.get("text") or "").strip().replace("\n", " ")
    if len(text) > max_len:
        return text[: max_len - 1] + "…"
    return text or "—"
