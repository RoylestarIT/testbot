"""Статус сервиса, история обновлений, вопросы WB, отчёт, feedback."""

from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from app.bot.ui import muted
from app.bot.utils.callbacks import answer_and_edit, safe_edit_message
from app.bot.product_news import build_release_history_text
from app.db.models import Marketplace, User as DbUser
from app.db.repositories.account import AccountRepository
from app.db.repositories.user import UserRepository
from app.db.session import get_session_factory
from app.services.marketplace.base import MarketplaceAPIError
from app.services.marketplace.wildberries import WildberriesClient
from app.services.monthly_report import build_monthly_report_text
from app.services.service_status import build_service_status_text

router = Router(name="product_maturity")

WB_SELLER_URL = "https://seller.wildberries.ru/"


def _back_more() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="◀️ Ещё", callback_data="menu:more")],
            [InlineKeyboardButton(text="🏠 Сводка", callback_data="menu:dashboard")],
        ]
    )


@router.callback_query(F.data == "menu:service_status")
async def menu_service_status(callback: CallbackQuery, db_user: DbUser) -> None:
    session_factory = get_session_factory()
    async with session_factory() as session:
        text = await build_service_status_text(session, db_user.id)
    await answer_and_edit(callback, text, reply_markup=_back_more())


@router.callback_query(F.data == "menu:changelog")
async def menu_changelog(callback: CallbackQuery) -> None:
    await answer_and_edit(callback, build_release_history_text(), reply_markup=_back_more())


@router.callback_query(F.data == "menu:monthly_report")
async def menu_monthly_report(callback: CallbackQuery, db_user: DbUser) -> None:
    session_factory = get_session_factory()
    async with session_factory() as session:
        text = await build_monthly_report_text(session, db_user.id)
    await answer_and_edit(callback, text, reply_markup=_back_more())


@router.callback_query(F.data == "menu:wb_questions")
async def menu_wb_questions(callback: CallbackQuery, db_user: DbUser) -> None:
    session_factory = get_session_factory()
    lines = ["❓ <b>Вопросы покупателей (WB)</b>", ""]
    async with session_factory() as session:
        accounts = await AccountRepository(session).list_by_user_id(db_user.id, active_only=True)
        wb_accounts = [a for a in accounts if a.marketplace == Marketplace.WB]
        if not wb_accounts:
            lines.append("Подключите 🟣 WB в ⚙️ Настройки.")
            await answer_and_edit(callback, "\n".join(lines), reply_markup=_back_more())
            return

        client = WildberriesClient()
        try:
            for acc in wb_accounts[:3]:
                name = acc.shop_name or f"#{acc.id}"
                try:
                    items = await client.list_unanswered_questions(acc, limit=3)
                except MarketplaceAPIError as exc:
                    lines.append(f"🟣 <b>{name}</b> — ⚠️ {exc}")
                    continue
                total = acc.cached_unanswered_questions
                lines.append(f"🟣 <b>{name}</b> — без ответа: <b>{total}</b>")
                if not items:
                    lines.append(muted("  Новых вопросов нет."))
                    continue
                for q in items:
                    text = (q.get("text") or "").strip().replace("\n", " ")
                    if len(text) > 120:
                        text = text[:117] + "…"
                    lines.append(f"  · {text or '—'}")
        finally:
            await client.aclose()

    lines.extend(
        [
            "",
            "<i>Ответ — в кабинете WB. Авто-ответы на вопросы в боте — в roadmap.</i>",
        ]
    )
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🌐 Кабинет WB", url=WB_SELLER_URL)],
            [InlineKeyboardButton(text="◀️ Ещё", callback_data="menu:more")],
        ]
    )
    await answer_and_edit(callback, "\n".join(lines), reply_markup=kb)


@router.callback_query(F.data.in_({"feedback:up", "feedback:down"}))
async def reply_feedback(callback: CallbackQuery, db_user: DbUser) -> None:
    session_factory = get_session_factory()
    positive = callback.data == "feedback:up"
    async with session_factory() as session:
        user = await UserRepository(session).get_by_id(db_user.id)
        if user is None:
            await callback.answer("Ошибка")
            return
        if positive:
            user.reply_feedback_up += 1
        else:
            user.reply_feedback_down += 1
        user.publish_actions_count = 0
        await session.commit()
    await callback.answer("Спасибо за оценку!" if positive else "Учтём, спасибо")
    if callback.message:
        await safe_edit_message(
            callback.message,
            "✅ Ответ отправлен. Оценка сохранена — помогает улучшать генерацию.",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="📬 Очередь", callback_data="review:mp:list")],
                ]
            ),
        )
