"""Визуальная система: читаемость в Telegram важнее «декора»."""

from __future__ import annotations

BRAND = "ReviewPilot"


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
    focus_line: str,
    focus_hint: str | None,
    detail_lines: list[str],
    footer: str | None = None,
) -> str:
    lines = [
        f"<b>{BRAND}</b>",
        "",
        focus_line,
    ]
    if focus_hint:
        lines.append(muted(focus_hint))
    if detail_lines:
        lines.append("")
        lines.extend(detail_lines)
    if footer:
        lines.append("")
        lines.append(muted(footer))
    return "\n".join(lines)


def review_stars(rating: int | str) -> str:
    if isinstance(rating, int) and 1 <= rating <= 5:
        return "★" * rating + "☆" * (5 - rating)
    return "—"


# --- совместимость со старыми экранами (упрощённые) ---


def brand_title(screen: str, *, tagline: str | None = None) -> str:
    if tagline:
        return f"<b>{BRAND}</b>\n<b>{screen}</b>\n{muted(tagline)}\n"
    return f"<b>{BRAND}</b> · <b>{screen}</b>\n\n"


def section(title: str) -> str:
    return f"\n<b>{title}</b>"


def bullet(text: str) -> str:
    return f"• {text}"


def kv(label: str, value: str) -> str:
    return f"{label}: <b>{value}</b>"


def footer_hint(text: str) -> str:
    return f"\n{muted(text)}"


def progress_bar(current: int, total: int, width: int = 6) -> str:
    if total <= 0:
        return ""
    filled = max(0, min(width, round(width * current / total)))
    return "▰" * filled + "▱" * (width - filled)


def tier_badge_free() -> str:
    return "Free"


def tier_badge_lite() -> str:
    return "Lite"


def tier_badge_pro() -> str:
    return "PRO"


def tier_badge_trial() -> str:
    return "Trial PRO"


def checklist_line(done: bool, label: str) -> str:
    mark = "✓" if done else "—"
    return f"{mark} {label}"
