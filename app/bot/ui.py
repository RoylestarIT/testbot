"""Премиальная визуальная система сообщений бота (Telegram HTML)."""

from __future__ import annotations

BRAND = "ReviewPilot"
DIVIDER = "────────────────"
DIVIDER_BOLD = "━━━━━━━━━━━━━━"


def brand_title(screen: str, *, tagline: str | None = None) -> str:
    head = f"✦ <b>{BRAND}</b>\n<b>{screen}</b>"
    if tagline:
        head += f"\n<i>{tagline}</i>"
    return f"{head}\n{DIVIDER_BOLD}"


def section(title: str) -> str:
    return f"\n<b>▎{title}</b>"


def bullet(text: str) -> str:
    return f"  • {text}"


def kv(label: str, value: str) -> str:
    return f"  {label}  <b>{value}</b>"


def quote(text: str) -> str:
    return f"<blockquote>{text}</blockquote>"


def muted(text: str) -> str:
    return f"<i>{text}</i>"


def footer_hint(text: str) -> str:
    return f"\n{DIVIDER}\n{muted(text)}"


def progress_bar(current: int, total: int, width: int = 8) -> str:
    if total <= 0:
        return ""
    filled = max(0, min(width, round(width * current / total)))
    bar = "▰" * filled + "▱" * (width - filled)
    return f"{bar}  {current}/{total}"


def tier_badge_free() -> str:
    return "◦ Free"


def tier_badge_lite() -> str:
    return "◆ Lite"


def tier_badge_pro() -> str:
    return "◆ PRO"


def tier_badge_trial() -> str:
    return "◇ Trial PRO"


def checklist_line(done: bool, label: str) -> str:
    mark = "✓" if done else "○"
    style = "" if done else "<i>"
    end = "" if done else "</i>"
    return f"  {mark} {style}{label}{end}"


def review_stars(rating: int | str) -> str:
    if isinstance(rating, int) and 1 <= rating <= 5:
        return "★" * rating + "☆" * (5 - rating)
    return "★ ★ ★ ★ ★"
