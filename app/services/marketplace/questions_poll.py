from __future__ import annotations

from dataclasses import dataclass

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Marketplace, MarketplaceAccount
from app.db.repositories.account import AccountRepository
from app.services.marketplace.base import MarketplaceAPIError
from app.services.marketplace.wildberries import WildberriesClient


@dataclass(slots=True)
class QuestionsNotify:
    shop_label: str
    new_count: int
    total_unanswered: int


async def refresh_unanswered_questions(
    session: AsyncSession,
    account: MarketplaceAccount,
    *,
    client: WildberriesClient | None = None,
) -> tuple[int, int]:
    """Обновляет счётчик на аккаунте. Возвращает (было, стало)."""
    if account.marketplace != Marketplace.WB:
        return account.cached_unanswered_questions, account.cached_unanswered_questions

    owns = client is None
    wb = client or WildberriesClient()
    previous = account.cached_unanswered_questions
    try:
        current = await wb.count_unanswered_questions(account)
    except MarketplaceAPIError as exc:
        logger.warning("Questions poll failed account_id={} err={}", account.id, exc)
        return previous, previous
    finally:
        if owns:
            await wb.aclose()

    account.cached_unanswered_questions = current
    await session.flush()
    return previous, current


def build_questions_notify(account: MarketplaceAccount, *, delta: int) -> QuestionsNotify:
    mp = "🟣" if account.marketplace == Marketplace.WB else "🔵"
    name = account.shop_name or "кабинет"
    return QuestionsNotify(
        shop_label=f"{mp} {name}",
        new_count=delta,
        total_unanswered=account.cached_unanswered_questions,
    )


def format_questions_message(items: list[QuestionsNotify]) -> str:
    lines = ["❓ <b>Новые вопросы покупателей</b>", ""]
    for item in items:
        if item.new_count > 0:
            lines.append(
                f"· {item.shop_label}: +<b>{item.new_count}</b> "
                f"(всего без ответа: <b>{item.total_unanswered}</b>)"
            )
    lines.append("")
    lines.append(
        "<i>Ответьте в кабинете WB/Ozon. Ответ на вопросы из бота — в разработке.</i>"
    )
    return "\n".join(lines)


async def poll_questions_for_accounts(
    session: AsyncSession,
    accounts: list[MarketplaceAccount],
) -> list[tuple[MarketplaceAccount, int]]:
    """Список (account, delta) где delta > 0."""
    deltas: list[tuple[MarketplaceAccount, int]] = []
    wb = WildberriesClient()
    try:
        for account in accounts:
            if account.marketplace != Marketplace.WB or not account.is_active:
                continue
            prev, cur = await refresh_unanswered_questions(session, account, client=wb)
            if cur > prev:
                deltas.append((account, cur - prev))
    finally:
        await wb.aclose()
    return deltas
