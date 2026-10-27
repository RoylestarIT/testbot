"""UI helpers for WB questions queue."""

from __future__ import annotations

from typing import Literal

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.bot.keyboards.nav import nav_back_details, nav_back_more
from app.db.models import MarketplaceAccount
from app.services.wb_questions_queue import format_question_preview, question_id_from_item

QuestionsBack = Literal["more", "details"]


def wb_questions_keyboard(
    *,
    items: list[tuple[MarketplaceAccount, dict]],
    page: int,
    has_more: bool,
    back: QuestionsBack = "more",
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
        prev = page - 1
        prev_cb = f"mp:questions:d:{prev}" if back == "details" else f"mp:questions:{prev}"
        nav.append(InlineKeyboardButton(text="◀️", callback_data=prev_cb))
    if has_more:
        nxt = page + 1
        nxt_cb = f"mp:questions:d:{nxt}" if back == "details" else f"mp:questions:{nxt}"
        nav.append(InlineKeyboardButton(text="▶️", callback_data=nxt_cb))
    if nav:
        rows.append(nav)
    rows.append(
        [
            InlineKeyboardButton(text="🟣 WB", url="https://seller.wildberries.ru/"),
            InlineKeyboardButton(text="🔵 Ozon", url="https://seller.ozon.ru/"),
        ]
    )
    back_kb = nav_back_details() if back == "details" else nav_back_more()
    rows.extend(back_kb.inline_keyboard)
    return InlineKeyboardMarkup(inline_keyboard=rows)
