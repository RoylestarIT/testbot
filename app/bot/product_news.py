"""Версионированные «Что нового» для существующих пользователей."""

from __future__ import annotations

from app.bot.ui import muted
from app.core.config import Settings
from app.db.models import User


def product_news_version(settings: Settings) -> str:
    return (settings.product_news_version or "").strip()


def user_should_see_product_news(user: User, settings: Settings) -> bool:
    version = product_news_version(settings)
    if not version:
        return False
    seen = (user.product_news_seen_version or "").strip()
    return seen != version


def build_product_news_banner(settings: Settings) -> str:
    return (
        "📣 <b>Что нового</b>\n"
        "· 📜 Политика и условия в боте — <code>/legal</code> или «⋯ Ещё → Документы»\n"
        "· 🧮 Калькулятор тарифа в «Подписка»\n"
        "· 📱 Удобнее калькулятор и экран принятия условий\n"
        + muted("Нажмите «Понятно», чтобы скрыть.")
    )
