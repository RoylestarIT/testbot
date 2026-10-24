from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.ui import brand_title, bullet, muted
from app.core.config import get_settings
from app.db.repositories.account import AccountRepository
from app.tasks.poller import format_ui_time, get_poller_health, get_poller_status_line


def _poller_summary() -> tuple[str, str]:
    health = get_poller_health()
    line = get_poller_status_line()
    last_ok = health.get("last_ok_at")
    if not last_ok:
        return "⏳", "Фоновая синхронизация ещё не выполнялась с момента запуска бота."
    err = health.get("last_error")
    if err:
        return "⚠️", f"Последний цикл sync: {line}\n{muted(f'Детали: {str(err)[:120]}')}"
    return "✅", f"Фоновая синхронизация: {line}"


async def build_service_status_text(session: AsyncSession, user_id: int) -> str:
    settings = get_settings()
    accounts = await AccountRepository(session).list_by_user_id(user_id)
    icon, poller_body = _poller_summary()

    lines = [
        brand_title("Статус сервиса", tagline="Синхронизация и ваши кабинеты", icon="🛰"),
        "",
        f"{icon}  <b>Маркетплейсы</b>",
        poller_body,
        "",
        f"⏱  Интервал опроса: <b>{settings.poll_interval_minutes}</b> мин",
        "",
        "<b>🏪 Ваши кабинеты</b>",
    ]

    if not accounts:
        lines.append(muted("Кабинеты не подключены — статус sync появится после подключения."))
    else:
        now = datetime.now(UTC)
        for acc in accounts[:10]:
            mp = "🟣 WB" if acc.marketplace.value == "wb" else "🔵 Ozon"
            name = acc.shop_name or f"#{acc.id}"
            if not acc.is_active:
                st = "⚠️ отключён"
            elif acc.last_sync_error:
                st = f"⚠️ {acc.last_sync_error[:60]}"
            elif acc.last_sync_at is None:
                st = "⏳ sync ещё не было"
            elif acc.last_sync_at < now - timedelta(hours=2):
                st = f"🕐 sync {format_ui_time(acc.last_sync_at)} — давно"
            else:
                st = f"✅ sync {format_ui_time(acc.last_sync_at)}"
            lines.append(bullet(f"{mp} <b>{name}</b> — {st}"))

    lines.extend(
        [
            "",
            muted("При сбоях API WB/Ozon очередь может обновляться с задержкой."),
            muted("Генерации ответов: локальная очередь LLM в этом же процессе бота."),
        ]
    )
    return "\n".join(lines)
