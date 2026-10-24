from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants import MANUAL_SHOP_NAME
from app.db.models import (
    GeneratedReply,
    Marketplace,
    MarketplaceAccount,
    Review,
    ReviewStatus,
    User,
)
from app.services.bot_activity import activity_snapshot
from app.services.start_sources import aggregate_start_sources


def _pct(part: int, whole: int) -> str:
    if whole <= 0:
        return "—"
    return f"{round(100 * part / whole)}%"


async def _users_with_first_reply(session: AsyncSession, user_ids: list[int]) -> int:
    if not user_ids:
        return 0
    stmt = (
        select(func.count(func.distinct(MarketplaceAccount.user_id)))
        .select_from(Review)
        .join(MarketplaceAccount, Review.account_id == MarketplaceAccount.id)
        .where(
            MarketplaceAccount.user_id.in_(user_ids),
            Review.status.in_((ReviewStatus.PROCESSED, ReviewStatus.PUBLISHED)),
        )
    )
    return int((await session.scalar(stmt)) or 0)


async def _median_hours_new_user_to_first_gen(session: AsyncSession, since: datetime) -> float | None:
    users = (
        await session.execute(
            select(User.id, User.created_at).where(
                User.created_at >= since,
                User.terms_accepted_at.isnot(None),
            )
        )
    ).all()
    if not users:
        return None
    deltas: list[float] = []
    for uid, created in users:
        if created is None:
            continue
        first_gen = await session.scalar(
            select(func.min(GeneratedReply.created_at))
            .select_from(GeneratedReply)
            .join(Review, GeneratedReply.review_id == Review.id)
            .join(MarketplaceAccount, Review.account_id == MarketplaceAccount.id)
            .where(MarketplaceAccount.user_id == uid)
        )
        if first_gen is None:
            continue
        c = created if created.tzinfo else created.replace(tzinfo=UTC)
        g = first_gen if first_gen.tzinfo else first_gen.replace(tzinfo=UTC)
        h = (g - c).total_seconds() / 3600.0
        if h >= 0:
            deltas.append(h)
    if not deltas:
        return None
    deltas.sort()
    mid = len(deltas) // 2
    if len(deltas) % 2:
        return round(deltas[mid], 1)
    return round((deltas[mid - 1] + deltas[mid]) / 2, 1)


async def build_admin_weekly_text(session: AsyncSession) -> str:
    now = datetime.now(UTC)
    d7 = now - timedelta(days=7)

    new_users = (
        await session.scalars(
            select(User.id).where(
                User.created_at >= d7,
                User.terms_accepted_at.isnot(None),
            )
        )
    ).all()
    new_ids = list(new_users)
    activated = await _users_with_first_reply(session, new_ids)

    wau_gen = int(
        (
            await session.scalar(
                select(func.count(func.distinct(MarketplaceAccount.user_id)))
                .select_from(GeneratedReply)
                .join(Review, GeneratedReply.review_id == Review.id)
                .join(MarketplaceAccount, Review.account_id == MarketplaceAccount.id)
                .where(GeneratedReply.created_at >= d7)
            )
        )
        or 0
    )

    median_ttw = await _median_hours_new_user_to_first_gen(session, d7)

    trial_ended = (
        await session.scalars(
            select(User).where(
                User.trial_pro_used.is_(True),
                User.trial_pro_until.isnot(None),
                User.trial_pro_until >= d7,
                User.trial_pro_until < now,
            )
        )
    ).all()
    trial_active_after = 0
    for u in trial_ended:
        if u.trial_pro_until is None:
            continue
        until = u.trial_pro_until if u.trial_pro_until.tzinfo else u.trial_pro_until.replace(tzinfo=UTC)
        gen_after = await session.scalar(
            select(func.count(GeneratedReply.id))
            .select_from(GeneratedReply)
            .join(Review, GeneratedReply.review_id == Review.id)
            .join(MarketplaceAccount, Review.account_id == MarketplaceAccount.id)
            .where(
                MarketplaceAccount.user_id == u.id,
                GeneratedReply.created_at > until,
            )
        )
        if gen_after and int(gen_after) > 0:
            trial_active_after += 1

    active_rows = await session.execute(
        select(MarketplaceAccount.user_id)
        .select_from(GeneratedReply)
        .join(Review, GeneratedReply.review_id == Review.id)
        .join(MarketplaceAccount, Review.account_id == MarketplaceAccount.id)
        .where(GeneratedReply.created_at >= d7)
        .distinct()
    )
    active_ids = [int(row[0]) for row in active_rows.all()]

    accounts_ok = 0
    accounts_total = 0
    sync_cutoff = now - timedelta(hours=48)
    if active_ids:
        accounts = (
            await session.scalars(
                select(MarketplaceAccount).where(
                    MarketplaceAccount.user_id.in_(active_ids),
                    MarketplaceAccount.marketplace.in_((Marketplace.WB, Marketplace.OZON)),
                )
            )
        ).all()
        for acc in accounts:
            if acc.shop_name == MANUAL_SHOP_NAME:
                continue
            accounts_total += 1
            err = (acc.last_sync_error or "").lower()
            if (
                acc.is_active
                and acc.last_sync_at is not None
                and (acc.last_sync_at if acc.last_sync_at.tzinfo else acc.last_sync_at.replace(tzinfo=UTC))
                >= sync_cutoff
                and "decrypt" not in err
                and not err.startswith("не удалось прочитать")
            ):
                accounts_ok += 1

    sources = await aggregate_start_sources(session)
    sources_line = ", ".join(f"{n}:{c}" for n, c in sources[:5]) if sources else "—"

    bot = activity_snapshot()
    lines = [
        "<b>📈 Неделя (ops)</b>",
        f"<i>Окно: последние 7 суток · {now.strftime('%d.%m.%Y %H:%M')} UTC</i>",
        "",
        "<b>1. Activation</b>",
        f"Новых с terms: <b>{len(new_ids)}</b> · первый ответ: <b>{activated}</b> ({_pct(activated, len(new_ids))})",
        "",
        "<b>2. Time-to-Wow</b>",
        f"Медиана до 1-й генерации (когорта новых): <b>{median_ttw if median_ttw is not None else '—'}</b> ч",
        "",
        "<b>3. WAU (генерации)</b>",
        f"Пользователей с ≥1 генерацией: <b>{wau_gen}</b>",
        "",
        "<b>4. После trial</b>",
        f"Trial закончился: <b>{len(trial_ended)}</b> · генерировали после: <b>{trial_active_after}</b> "
        f"({_pct(trial_active_after, len(trial_ended))})",
        "",
        "<b>5. Кабинеты (активные)</b>",
        f"Sync OK за 48 ч: <b>{accounts_ok}</b> / <b>{accounts_total}</b> ({_pct(accounts_ok, accounts_total)})",
        "",
        "<b>/start источники (всего)</b>",
        sources_line,
        "",
        "<b>Telegram (этот процесс)</b>",
        f"Updates с boot: <b>{bot.get('updates_since_boot')}</b> · "
        f"последний: <b>{bot.get('last_update_minsk') or '—'}</b>",
        "",
        "<i>Оплату и MRR смотри отдельно. Eval: scripts/eval_reply_drafts.py</i>",
    ]
    return "\n".join(lines)
