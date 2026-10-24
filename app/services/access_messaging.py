"""Понятные формулировки Free / Trial / Lite / PRO (без деталей оплаты)."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.db.models import Subscription, SubscriptionPlan, SubscriptionStatus, User
from app.services.pro_access import is_trial_pro_active


def trial_pro_activated_text(user: User, settings: Settings | None = None) -> str:
    settings = settings or get_settings()
    until = user.trial_pro_until.strftime("%d.%m.%Y") if user.trial_pro_until else "—"
    reserve = user.free_api_publishes_remaining
    return (
        f"🎁 <b>Trial PRO</b> до <b>{until}</b> ({settings.trial_pro_days} дн.)\n\n"
        "Сейчас: <b>publish в WB/Ozon из бота</b> и авто только на <b>4–5★</b> — без лимита.\n\n"
        "После trial без PRO/Lite:\n"
        "· Free — до 5 генераций/день, ответ копированием;\n"
        "· Lite — ∞ генераций, копия в кабинет;\n"
        "· PRO — снова publish из бота.\n\n"
        f"<i>Запас пробных publish на Free (на после trial): <b>{reserve}</b> — "
        "не расходуется, пока trial активен.</i>"
    )


async def build_dashboard_publish_line(
    session: AsyncSession,
    user: User,
    subscription: Subscription | None,
) -> str | None:
    if subscription and subscription.status == SubscriptionStatus.ACTIVE:
        if subscription.plan == SubscriptionPlan.PRO:
            return "🚀  PRO: publish в API + авто 4–5★"
        return "✨  Lite: ∞ генераций · ответ — копированием в кабинет"

    if await is_trial_pro_active(user):
        until = user.trial_pro_until.strftime("%d.%m.%Y") if user.trial_pro_until else "—"
        return f"🎁  Trial PRO до {until} · publish без лимита"

    if user.free_api_publishes_remaining > 0:
        return (
            f"🚀  Пробных publish: <b>{user.free_api_publishes_remaining}</b> "
            "(Free · или trial PRO на сводке)"
        )
    return "📋  Publish в API — trial PRO или тариф PRO"


def build_my_access_publish_block(
    user: User,
    subscription: Subscription | None,
    *,
    trial_active: bool,
) -> list[str]:
    from app.bot.ui import bullet, muted

    lines: list[str] = []
    if subscription and subscription.status == SubscriptionStatus.ACTIVE:
        if subscription.plan == SubscriptionPlan.PRO:
            lines.append(bullet("Publish в API + авто 4–5★: <b>да</b>"))
        else:
            lines.append(bullet("Publish в API: <b>копирование</b> в кабинет (Lite)"))
        return lines

    if trial_active:
        until = user.trial_pro_until.strftime("%d.%m.%Y") if user.trial_pro_until else "—"
        lines.append(bullet(f"Trial PRO до <b>{until}</b> — publish без лимита"))
        lines.append(
            muted(
                f"После trial: Lite = копия, PRO = publish. "
                f"Запас на Free: {user.free_api_publishes_remaining} publish."
            )
        )
        return lines

    lines.append(bullet("Publish в API: <b>PRO</b>, trial или пробная квота"))
    if user.free_api_publishes_remaining:
        lines.append(bullet(f"Пробных publish осталось: <b>{user.free_api_publishes_remaining}</b>"))
    return lines
