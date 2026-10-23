from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from app.bot.copy import HELP_TEXT, TERMS_TEXT, WELCOME_TEXT
from app.bot.keyboards.menu import main_menu_keyboard
from app.core.config import get_settings
from app.db.models import User as DbUser
from app.db.repositories.user import UserRepository
from app.db.session import get_session_factory

router = Router(name="start")


def _terms_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Принимаю", callback_data="onboarding:accept")],
        ]
    )


def _needs_terms(db_user: DbUser) -> bool:
    return db_user.terms_accepted_at is None


def _show_admin_menu(tg_id: int) -> bool:
    return tg_id in get_settings().admin_ids


@router.message(CommandStart())
async def cmd_start(message: Message, db_user: DbUser) -> None:
    if _needs_terms(db_user):
        await message.answer(TERMS_TEXT, reply_markup=_terms_keyboard())
        return
    tg_id = message.from_user.id if message.from_user else 0
    await message.answer(
        f"{WELCOME_TEXT}\n\nВыберите раздел в меню:",
        reply_markup=main_menu_keyboard(show_admin=_show_admin_menu(tg_id)),
    )


@router.callback_query(F.data == "onboarding:accept")
async def onboarding_accept(callback: CallbackQuery, db_user: DbUser) -> None:
    session_factory = get_session_factory()
    async with session_factory() as session:
        await UserRepository(session).accept_terms(db_user.id)
        await session.commit()
    await callback.answer("Спасибо!")
    if callback.message:
        tg_id = callback.from_user.id if callback.from_user else 0
        await callback.message.edit_text(
            f"{WELCOME_TEXT}\n\nВыберите раздел в меню:",
            reply_markup=main_menu_keyboard(show_admin=_show_admin_menu(tg_id)),
        )


@router.callback_query(F.data == "menu:help")
async def menu_help(callback: CallbackQuery) -> None:
    await callback.answer()
    if callback.message:
        await callback.message.edit_text(HELP_TEXT, reply_markup=main_menu_keyboard())
