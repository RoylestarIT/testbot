"""Понятные формулировки Free / Trial / Lite / PRO (без деталей оплаты)."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.db.models import Subscription, SubscriptionPlan, SubscriptionStatus, User
from app.services.pro_access import is_trial_pro_active


def trial_ended_screen_text(user: User) -> str:
    reserve = user.free_api_publishes_remaining
    return (
        "⏱ <b>Пробный PRO закончился</b>\n\n"
        "Что изменилось:\n"
        "· Отправка ответа из бота — снова только на тарифе <b>PRO</b>\n"
        "· На <b>бесплатном тарифе</b> — до 5 подготовленных ответов в день, дальше копируете в кабинет\n"
        "· На <b>Lite</b> — без дневного лимита, тоже копирование в кабинет\n\n"
        f"Пробных отправок из бота на бесплатном тарифе (если не тратили): <b>{reserve}</b>\n\n"
        "<i>Низкие оценки по-прежнему только вы · авто на 4–5★ было на PRO.</i>"
    )


def trial_pro_activated_text(user: User, settings: Settings | None = None) -> str:
    settings = settings or get_settings()
    until = user.trial_pro_until.strftime("%d.%m.%Y") if user.trial_pro_until else "—"
    reserve = user.free_api_publishes_remaining
    return (
        f"🎁 <b>Пробный PRO</b> до <b>{until}</b> ({settings.trial_pro_days} дн.)\n\n"
        "Сейчас можно отправлять ответы из бота в WB/Ozon и включить авто-ответы на <b>4–5★</b>.\n\n"
        "После окончания пробного периода:\n"
        "· Бесплатно — до 5 ответов в день, копирование в кабинет;\n"
        "· Lite — без лимита, копирование;\n"
        "· PRO — снова отправка из бота.\n\n"
        f"<i>Пробные отправки на бесплатном тарифе после пробного периода: <b>{reserve}</b> "
        "(не тратятся, пока пробный PRO активен).</i>"
    )


async def build_dashboard_publish_line(
    session: AsyncSession,
    user: User,
    subscription: Subscription | None,
) -> str | None:
    if subscription and subscription.status == SubscriptionStatus.ACTIVE:
        if subscription.plan == SubscriptionPlan.PRO:
            return "🚀  PRO: отправка из бота + авто на 4–5★"
        return "✨  Lite: без лимита ответов · копируете в кабинет"

    if await is_trial_pro_active(user):
        until = user.trial_pro_until.strftime("%d.%m.%Y") if user.trial_pro_until else "—"
        return f"🎁  Пробный PRO до {until}"

    if user.free_api_publishes_remaining > 0:
        return (
            f"🚀  Пробных отправок из бота: <b>{user.free_api_publishes_remaining}</b> "
            "(бесплатный тариф или кнопка пробного PRO на сводке)"
        )
    return "📋  Отправка из бота — пробный или тариф PRO"


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
            lines.append(bullet("Отправка из бота + авто 4–5★: <b>да</b>"))
        else:
            lines.append(bullet("Отправка из бота: <b>копирование</b> в кабинет (Lite)"))
        return lines

    if trial_active:
        until = user.trial_pro_until.strftime("%d.%m.%Y") if user.trial_pro_until else "—"
        lines.append(bullet(f"Пробный PRO до <b>{until}</b>"))
        lines.append(
            muted(
                f"После пробного периода: Lite — копия, PRO — из бота. "
                f"Запас на бесплатном тарифе: {user.free_api_publishes_remaining} отправок."
            )
        )
        return lines

    lines.append(bullet("Отправка из бота: <b>PRO</b>, пробный период или пробная квота"))
    if user.free_api_publishes_remaining:
        lines.append(bullet(f"Пробных отправок осталось: <b>{user.free_api_publishes_remaining}</b>"))
    return lines
