from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from app.bot.copy import TERMS_TEXT
from app.bot.keyboards.legal import legal_document_keyboard, legal_hub_keyboard, parse_legal_back
from app.bot.keyboards.terms import terms_acceptance_keyboard
from app.bot.handlers.support import support_keyboard, support_screen_text
from app.bot.legal.documents import LegalDocKind, document_page
from app.bot.ui import brand_title, muted, section
from app.bot.utils.callbacks import safe_edit_message
from app.core.config import get_settings

router = Router(name="legal")


def _parse_legal_callback(data: str) -> tuple[LegalDocKind, int] | None:
    parts = data.split(":")
    if len(parts) not in (3, 4) or parts[0] != "legal":
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


def _legal_hub_text() -> str:
    return (
        brand_title("Документы", tagline="Политика и условия сервиса", icon="📜")
        + section("В боте", icon="📱")
        + "\n"
        + muted(
            "Полные тексты адаптированы под «Голос бренда»: WB/Ozon, подписка Lite/PRO, "
            "обработка отзывов и ИИ-ответы."
        )
    )


async def _show_legal_hub(message_or_callback) -> None:
    text = _legal_hub_text()
    markup = legal_hub_keyboard()
    if isinstance(message_or_callback, Message):
        await message_or_callback.answer(text, reply_markup=markup)
        return
    await message_or_callback.answer()
    if message_or_callback.message:
        await safe_edit_message(message_or_callback.message, text, reply_markup=markup)


@router.message(Command("legal"))
async def cmd_legal(message: Message) -> None:
    await _show_legal_hub(message)


@router.callback_query(F.data == "menu:legal")
async def menu_legal(callback: CallbackQuery) -> None:
    await _show_legal_hub(callback)


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


@router.callback_query(F.data == "legal:back:menu")
async def legal_back_to_menu(callback: CallbackQuery) -> None:
    await callback.answer()
    if callback.message:
        await safe_edit_message(
            callback.message,
            _legal_hub_text(),
            reply_markup=legal_hub_keyboard(),
        )


@router.callback_query(F.data == "legal:back:support")
async def legal_back_to_support(callback: CallbackQuery) -> None:
    await callback.answer()
    if callback.message:
        await safe_edit_message(
            callback.message,
            support_screen_text(),
            reply_markup=support_keyboard(),
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
    back = parse_legal_back(callback.data)
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
            reply_markup=legal_document_keyboard(kind, page_index, settings=settings, back=back),
        )
