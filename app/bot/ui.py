"""Визуальная система: читаемость в Telegram важнее «декора»."""

from __future__ import annotations

BRAND = "Голос бренда"
ICON = "✨"

# Единая формулировка раздела ответов (не «очередь» / «ответить» по отдельности)
REVIEWS_HUB_BUTTON = "📬 Ответы на отзывы"

def muted(text: str) -> str:
    return f"<i>{text}</i>"


def quote(text: str) -> str:
    return f"<blockquote>{text}</blockquote>"


def screen_simple(title: str, *paragraphs: str) -> str:
    """Заголовок + абзацы через пустую строку."""
    parts = [f"<b>{title}</b>", ""]
    parts.extend(paragraphs)
    return "\n".join(p for p in parts if p is not None)


def dashboard_home(
    *,
    status_block: str,
    meta_lines: list[str],
    nudge: str | None = None,
    footer: str | None = None,
) -> str:
    """Сводка: шапка бренда → статус → компактные факты (без маркeting-блоков)."""
    sep = "───────────────"
    lines = [f"{ICON} <b>{BRAND}</b>", sep, "", status_block]
    if meta_lines:
        lines.extend(["", sep, ""])
        lines.extend(meta_lines)
    if nudge:
        lines.extend(["", nudge])
    if footer:
        lines.extend(["", muted(footer)])
    return "\n".join(lines)


def review_stars(rating: int | str) -> str:
    if isinstance(rating, int) and 1 <= rating <= 5:
        return "★" * rating + "☆" * (5 - rating)
    return "—"


# --- совместимость со старыми экранами (упрощённые) ---


def brand_title(screen: str, *, tagline: str | None = None, icon: str = ICON) -> str:
    if tagline:
        return f"{icon} <b>{BRAND}</b>\n<b>{screen}</b>\n{muted(tagline)}\n"
    return f"{icon} <b>{BRAND}</b> · <b>{screen}</b>\n\n"


def section(title: str, *, icon: str = "") -> str:
    prefix = f"{icon} " if icon else ""
    return f"\n\n<b>{prefix}{title}</b>\n\n"


def bullet(text: str, *, icon: str = "▫️") -> str:
    return f"{icon} {text}"


def bullet_list(*items: str) -> str:
    """Пункты списка с пустой строкой между ними (читаемость в Telegram)."""
    return "\n\n".join(bullet(item) for item in items)


def kv(label: str, value: str) -> str:
    return f"{label}: <b>{value}</b>"


def footer_hint(text: str) -> str:
    return f"\n{muted(text)}"


VISUAL_SEP = "───────────────"


def hero_quote(text: str) -> str:
    """Акцентный блок в начале экрана."""
    return quote(text.strip()) + "\n\n"


def progress_bar(current: int, total: int, width: int = 6) -> str:
    if total <= 0:
        return ""
    filled = max(0, min(width, round(width * current / total)))
    return "▰" * filled + "▱" * (width - filled)


def tier_badge_free() -> str:
    return "🆓 Free"


def tier_badge_lite() -> str:
    return "✨ Lite"


def tier_badge_pro() -> str:
    return "💎 PRO"


def tier_badge_trial() -> str:
    return "🎁 Trial PRO"


def checklist_line(done: bool, label: str) -> str:
    mark = "✅" if done else "⬜"
    return f"{mark} {label}"
