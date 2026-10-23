from __future__ import annotations

from dataclasses import dataclass, field

from app.bot.ui import BRAND, ICON


@dataclass
class PollerUserNotify:
    auto_published: int = 0
    queue_new: int = 0
    queue_negative: int = 0
    auto_failed: int = 0
    auto_previews: list[str] = field(default_factory=list)


def build_poller_notify_text(*, stats: PollerUserNotify, negative_only: bool) -> str | None:
    if negative_only:
        if stats.queue_negative <= 0:
            return None
        return (
            f"{ICON} <b>{BRAND}</b>\n"
            f"⚠️ Негативных отзывов (1–3★): <b>{stats.queue_negative}</b>\n"
            "<i>Рекомендуем ответить в первую очередь.</i>"
        )

    if stats.auto_published <= 0 and stats.queue_new <= 0 and stats.auto_failed <= 0:
        return None

    lines = [f"{ICON} <b>{BRAND}</b>"]
    if stats.auto_published > 0:
        lines.append(f"🤖 Авто-ответов (PRO): <b>{stats.auto_published}</b>")
        if stats.auto_previews:
            sample = stats.auto_previews[0]
            if len(sample) > 80:
                sample = sample[:77] + "…"
            lines.append(muted_preview(sample))
    if stats.queue_new > 0:
        neg = f", из них негатив 1–3★: <b>{stats.queue_negative}</b>" if stats.queue_negative else ""
        lines.append(f"✋ В очереди: <b>{stats.queue_new}</b>{neg}")
    if stats.auto_failed > 0:
        lines.append(f"⚠️ Не удалось авто-ответить: <b>{stats.auto_failed}</b> — откройте очередь.")
    if stats.queue_new > 0:
        lines.append("<i>Откройте очередь и ответьте в выбранном тоне.</i>")
    elif stats.auto_published > 0:
        lines.append("<i>Позитивные отзывы уже закрыты автоматически.</i>")
    return "\n".join(lines)


def muted_preview(text: str) -> str:
    return f"<i>«{text}»</i>"
