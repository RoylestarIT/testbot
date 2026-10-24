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
from app.services.wb_questions_queue import (
    filter_visible_questions,
    format_question_preview,
    question_id_from_item,
    snooze_question,
)
from app.bot.handlers.wb_questions_ui import wb_questions_keyboard
from app.bot.user_errors import user_error_from_exception

router = Router(name="product_maturity")

WB_QUESTIONS_PAGE_SIZE = 5

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


async def _render_wb_questions(callback: CallbackQuery, db_user: DbUser, page: int) -> None:
    session_factory = get_session_factory()
    page = max(0, page)
    lines = [
        "❓ <b>Вопросы покупателей (WB)</b>",
        muted("Очередь как у отзывов: ⏰ — отложить на 24 ч. Ответ — в кабинете WB."),
        "",
    ]
    flat: list[tuple] = []
    async with session_factory() as session:
        user = await UserRepository(session).get_by_id(db_user.id)
        if user is None:
            await callback.answer("Ошибка профиля", show_alert=True)
            return
        accounts = await AccountRepository(session).list_by_user_id(db_user.id, active_only=True)
        wb_accounts = [a for a in accounts if a.marketplace == Marketplace.WB]
        if not wb_accounts:
            lines.append("Подключите 🟣 WB в ⚙️ Настройки.")
            await answer_and_edit(callback, "\n".join(lines), reply_markup=_back_more())
            return

        client = WildberriesClient()
        try:
            for acc in wb_accounts[:5]:
                name = acc.shop_name or f"#{acc.id}"
                try:
                    raw = await client.list_unanswered_questions(acc, limit=20)
                    visible = filter_visible_questions(user, acc, raw)
                except MarketplaceAPIError as exc:
                    err = user_error_from_exception(exc)
                    lines.append(f"🟣 <b>{name}</b> — {err.html[:200]}")
                    continue
                except Exception as exc:
                    err = user_error_from_exception(exc)
                    lines.append(f"🟣 <b>{name}</b> — ⚠️")
                    continue
                total = acc.cached_unanswered_questions
                lines.append(f"🟣 <b>{name}</b> — без ответа: <b>{total}</b> (в очереди: {len(visible)})")
                for item in visible:
                    flat.append((acc, item))
            await session.commit()
        finally:
            await client.aclose()

    start = page * WB_QUESTIONS_PAGE_SIZE
    chunk = flat[start : start + WB_QUESTIONS_PAGE_SIZE]
    has_more = len(flat) > start + WB_QUESTIONS_PAGE_SIZE

    if not flat:
        lines.append(muted("Нет активных вопросов (или все отложены)."))
    else:
        lines.append("")
        for acc, item in chunk:
            preview = format_question_preview(item)
            lines.append(f"· {preview}")

    kb = wb_questions_keyboard(items=chunk, page=page, has_more=has_more)
    await answer_and_edit(callback, "\n".join(lines), reply_markup=kb)


@router.callback_query(F.data == "menu:wb_questions")
async def menu_wb_questions(callback: CallbackQuery, db_user: DbUser) -> None:
    await _render_wb_questions(callback, db_user, page=0)


@router.callback_query(F.data.regexp(r"^wb:questions:\d+$"))
async def wb_questions_page(callback: CallbackQuery, db_user: DbUser) -> None:
    page = int(callback.data.split(":")[-1])
    await _render_wb_questions(callback, db_user, page=page)


@router.callback_query(F.data.regexp(r"^wb:q:snooze:\d+:.+$"))
async def wb_question_snooze(callback: CallbackQuery, db_user: DbUser) -> None:
    parts = callback.data.split(":", 4)
    if len(parts) < 5:
        await callback.answer("Ошибка")
        return
    account_id = int(parts[3])
    question_id = parts[4]
    session_factory = get_session_factory()
    async with session_factory() as session:
        user = await UserRepository(session).get_by_id(db_user.id)
        if user is None:
            await callback.answer("Ошибка")
            return
        snooze_question(user, account_id, question_id)
        await session.commit()
    await callback.answer("Отложено на 24 ч")
    await _render_wb_questions(callback, db_user, page=0)


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
