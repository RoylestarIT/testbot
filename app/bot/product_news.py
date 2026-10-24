"""Версионированные «Что нового» и история обновлений."""

from __future__ import annotations

from app.bot.ui import muted
from app.core.config import Settings
from app.db.models import User

RELEASE_NOTES: list[dict[str, object]] = [
    {
        "version": "2025-10-v1",
        "title": "Октябрь 2025",
        "items": [
            "📜 Политика и условия в боте — /legal",
            "🧮 Калькулятор тарифа в «Подписка»",
            "📱 Удобнее экран принятия условий",
        ],
    },
    {
        "version": "2025-10-v2",
        "title": "Зрелость продукта",
        "items": [
            "🛰 Статус сервиса и синхронизации",
            "🆘 Обращение в поддержку из бота",
            "📋 Чеклист быстрого старта на сводке",
            "⭐ Telegram Stars и USDT в Crypto Bot",
        ],
    },
    {
        "version": "2026-10-v1",
        "title": "Октябрь 2026",
        "items": [
            "🩺 Здоровье аккаунта и понятный trial/PRO",
            "❓ Вопросы WB/Ozon — очередь и snooze",
            "🧮 Калькулятор: hub, Stars, кнопки с ценой",
            "📈 Админ: экран «Неделя» (activation, WAU, кабинеты)",
        ],
    },
]


def product_news_version(settings: Settings) -> str:
    return (settings.product_news_version or "").strip()


def user_should_see_product_news(user: User, settings: Settings) -> bool:
    version = product_news_version(settings)
    if not version:
        return False
    seen = (user.product_news_seen_version or "").strip()
    return seen != version


def _notes_for_version(version: str) -> dict[str, object] | None:
    for entry in RELEASE_NOTES:
        if entry.get("version") == version:
            return entry
    return None


def build_product_news_banner(settings: Settings) -> str:
    version = product_news_version(settings)
    entry = _notes_for_version(version)
    lines = ["📣 <b>Что нового</b>"]
    if entry:
        for item in entry.get("items", []):
            lines.append(f"· {item}")
    else:
        lines.append("· Обновления описаны в «История обновлений».")
    lines.append(muted("Нажмите «Понятно», чтобы скрыть."))
    return "\n".join(lines)


def build_release_history_text() -> str:
    lines = ["📜 <b>История обновлений</b>", ""]
    for entry in RELEASE_NOTES:
        title = entry.get("title", entry.get("version", ""))
        ver = entry.get("version", "")
        lines.append(f"<b>{title}</b>  <code>{ver}</code>")
        for item in entry.get("items", []):
            lines.append(f"· {item}")
        lines.append("")
    lines.append(muted("Текущая версия баннера задаётся PRODUCT_NEWS_VERSION на сервере."))
    return "\n".join(lines).strip()
