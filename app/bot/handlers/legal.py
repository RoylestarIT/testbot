from aiogram import F, Router
from aiogram.types import CallbackQuery

from app.bot.copy import TERMS_TEXT
from app.bot.keyboards.legal import legal_document_keyboard
from app.bot.keyboards.terms import terms_acceptance_keyboard
from app.bot.legal.documents import LegalDocKind, document_page
from app.bot.utils.callbacks import safe_edit_message
from app.core.config import get_settings

router = Router(name="legal")


def _parse_legal_callback(data: str) -> tuple[LegalDocKind, int] | None:
    parts = data.split(":")
    if len(parts) != 3 or parts[0] != "legal":
        return None
    try:
        page = int(parts[2])
    except ValueError:
        return None
    if parts[1] == LegalDocKind.PRIVACY.value:
        return LegalDocKind.PRIVACY, page
    if parts[1] == LegalDocKind.TERMS.value:
        return LegalDocKind.TERMS, page
    return None


@router.callback_query(F.data == "legal:noop")
async def legal_noop(callback: CallbackQuery) -> None:
    await callback.answer()


@router.callback_query(F.data == "legal:back:accept")
async def legal_back_to_accept(callback: CallbackQuery) -> None:
    await callback.answer()
    if callback.message:
        await safe_edit_message(
            callback.message,
            TERMS_TEXT,
            reply_markup=terms_acceptance_keyboard(),
        )


@router.callback_query(F.data.startswith("legal:privacy:") | F.data.startswith("legal:terms:"))
async def legal_show_page(callback: CallbackQuery) -> None:
    if callback.data is None:
        return
    parsed = _parse_legal_callback(callback.data)
    if parsed is None:
        await callback.answer()
        return
    kind, page_index = parsed
    settings = get_settings()
    text = document_page(kind, page_index, settings)
    if text is None:
        await callback.answer("Страница не найдена", show_alert=True)
        return
    await callback.answer()
    if callback.message:
        await safe_edit_message(
            callback.message,
            text,
            reply_markup=legal_document_keyboard(kind, page_index, settings=settings),
        )
