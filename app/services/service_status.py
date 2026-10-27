from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.ui import SYNC_BUTTON, brand_title, bullet, muted, quote
from app.constants import MANUAL_SHOP_NAME
from app.core.config import get_settings
from app.core.datetime_utils import as_utc
from app.db.models import Marketplace, MarketplaceAccount, Review, ReviewStatus
from app.db.repositories.account import AccountRepository
from app.tasks.poller import format_ui_time, get_poller_health, get_poller_status_line


def _poller_summary() -> tuple[str, str]:
    health = get_poller_health()
    line = get_poller_status_line()
    last_ok = health.get("last_ok_at")
    if not last_ok:
        return "⏳", "Синхронизация ещё не выполнялась с момента запуска бота."
    err = health.get("last_error")
    if err:
        return "⚠️", f"Последний цикл: {line}\n{muted(f'Детали: {str(err)[:120]}')}"
    return "✅", f"Последняя синхронизация: {line}"


def _account_issue(acc: MarketplaceAccount, now: datetime) -> str | None:
    err = (acc.last_sync_error or "").lower()
    if not acc.is_active:
        return "отключён"
    if "decrypt" in err or "ключ" in err and "прочит" in err:
        return "ключ не читается — переподключите в настройках"
    if acc.last_sync_error:
        return acc.last_sync_error[:80]
    if acc.last_sync_at is None:
        return f"ещё не синхронизировали — нажмите «{SYNC_BUTTON}» на сводке"
    last_sync = as_utc(acc.last_sync_at)
    if last_sync is not None and last_sync < now - timedelta(hours=2):
        return f"давно не обновлялось — проверьте ключ или «{SYNC_BUTTON}»"
    return None


async def _new_reviews_count(session: AsyncSession, user_id: int) -> int:
    now = datetime.now(UTC)
    return int(
        (
            await session.scalar(
                select(func.count(Review.id))
                .select_from(Review)
                .join(MarketplaceAccount, Review.account_id == MarketplaceAccount.id)
                .where(
                    MarketplaceAccount.user_id == user_id,
                    Review.status == ReviewStatus.NEW,
                    (Review.snoozed_until.is_(None)) | (Review.snoozed_until <= now),
                    MarketplaceAccount.shop_name != MANUAL_SHOP_NAME,
                )
            )
        )
        or 0
    )


async def build_service_status_text(session: AsyncSession, user_id: int) -> str:
    settings = get_settings()
    accounts = await AccountRepository(session).list_by_user_id(user_id)
    api_accounts = [
        a
        for a in accounts
        if a.marketplace in (Marketplace.WB, Marketplace.OZON)
        and (a.shop_name is None or a.shop_name != MANUAL_SHOP_NAME)
    ]
    icon, poller_body = _poller_summary()
    now = datetime.now(UTC)
    issues = [_account_issue(a, now) for a in api_accounts]
    issue_count = sum(1 for i in issues if i is not None)
    poller_bad = icon != "✅"
    queue_n = await _new_reviews_count(session, user_id)

    if not api_accounts:
        headline = "⬜  Подключите кабинет WB или Ozon в настройках"
    elif issue_count == 0 and not poller_bad:
        headline = "✅  Всё работает — бот получает отзывы и готов к ответам"
    elif issue_count and poller_bad:
        headline = f"⚠️  {issue_count} кабинет(ов) и фоновая синхронизация требуют внимания"
    elif issue_count:
        headline = f"⚠️  Проверьте {issue_count} кабинет(ов) — см. ниже"
    else:
        headline = f"⚠️  Фоновая синхронизация — сбой, нажмите «{SYNC_BUTTON}» на сводке"

    lines = [
        brand_title("Здоровье аккаунта", tagline="Почему бот молчит или нет отзывов", icon="🩺"),
        "",
        quote(headline),
        "",
        f"📬  В очереди ответов: <b>{queue_n}</b>",
        "",
        f"{icon}  <b>Синхронизация</b>",
        poller_body,
        "",
        f"⏱  Интервал опроса: <b>{settings.poll_interval_minutes}</b> мин",
        "",
        "<b>🏪 Ваши кабинеты</b>",
    ]

    if not api_accounts:
        lines.append(muted("Пока не подключены — статус появится после добавления ключа кабинета."))
    else:
        for acc, issue in zip(api_accounts[:10], issues[:10], strict=False):
            mp = "🟣 WB" if acc.marketplace.value == "wb" else "🔵 Ozon"
            name = acc.shop_name or f"#{acc.id}"
            if issue is None:
                st = f"✅ {format_ui_time(acc.last_sync_at)}"
            else:
                st = f"⚠️ {issue}"
            lines.append(bullet(f"{mp} <b>{name}</b> — {st}"))

    lines.extend(
        [
            "",
            muted(
                "Бот не отвечает в чате — чаще всего запущена вторая копия с тем же токеном "
                "или нет сети на сервере."
            ),
            muted(
                "Ошибка ключа — ⚙️ Настройки → кабинет → обновите ключ или подключите заново."
            ),
            muted("При сбоях WB/Ozon отзывы в очереди обновляются с небольшой задержкой."),
        ]
    )
    return "\n".join(lines)
