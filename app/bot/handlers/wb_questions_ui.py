"""UI helpers for WB questions queue."""

from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.db.models import MarketplaceAccount
from app.services.wb_questions_queue import format_question_preview, question_id_from_item


def wb_questions_keyboard(
    *,
    items: list[tuple[MarketplaceAccount, dict]],
    page: int,
    has_more: bool,
) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for acc, item in items:
        qid = question_id_from_item(item)
        if not qid:
            continue
        preview = format_question_preview(item, max_len=28)
        rows.append(
            [
                InlineKeyboardButton(
                    text=f"⏰ {preview}",
                    callback_data=f"mp:q:snooze:{acc.id}:{qid}",
                )
            ]
        )
    nav: list[InlineKeyboardButton] = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="◀️", callback_data=f"mp:questions:{page - 1}"))
    if has_more:
        nav.append(InlineKeyboardButton(text="▶️", callback_data=f"mp:questions:{page + 1}"))
    if nav:
        rows.append(nav)
    rows.append(
        [
            InlineKeyboardButton(text="🟣 WB", url="https://seller.wildberries.ru/"),
            InlineKeyboardButton(text="🔵 Ozon", url="https://seller.ozon.ru/"),
        ]
    )
    rows.append(
        [
            InlineKeyboardButton(text="◀️ Ещё", callback_data="menu:more"),
            InlineKeyboardButton(text="🏠 Сводка", callback_data="menu:dashboard"),
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)
