from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from app.bot.copy import HELP_TEXT, TERMS_TEXT
from app.bot.keyboards.terms import terms_acceptance_keyboard
from app.bot.ui import BRAND, ICON
from app.bot.handlers.dashboard import _edit_dashboard, _send_dashboard
from app.bot.keyboards.menu import main_menu_keyboard, more_menu_keyboard
from app.core.config import get_settings
from app.db.models import User as DbUser
from app.db.repositories.user import UserRepository
from app.db.session import get_session_factory

router = Router(name="start")


def _needs_terms(db_user: DbUser) -> bool:
    return db_user.terms_accepted_at is None


def _show_admin_menu(tg_id: int) -> bool:
    return tg_id in get_settings().admin_ids


async def _home_keyboard(db_user_id: int, tg_id: int) -> InlineKeyboardMarkup:
    session_factory = get_session_factory()
    async with session_factory() as session:
        user = await UserRepository(session).get_by_id(db_user_id)
        show_onboarding = user is not None and user.onboarding_completed_at is None
    kb = main_menu_keyboard(show_admin=_show_admin_menu(tg_id))
    if not show_onboarding:
        return kb
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🚀 Начать настройку", callback_data="menu:onboarding")],
            *kb.inline_keyboard,
        ]
    )


@router.message(CommandStart())
async def cmd_start(message: Message, db_user: DbUser) -> None:
    if _needs_terms(db_user):
        await message.answer(TERMS_TEXT, reply_markup=terms_acceptance_keyboard())
        return
    await _send_dashboard(message, db_user)


@router.callback_query(F.data == "onboarding:accept")
async def onboarding_accept(callback: CallbackQuery, db_user: DbUser) -> None:
    session_factory = get_session_factory()
    async with session_factory() as session:
        await UserRepository(session).accept_terms(db_user.id)
        await session.commit()
    await callback.answer("Спасибо!")
    if callback.message:
        await _edit_dashboard(callback.message, db_user)


@router.callback_query(F.data.in_({"menu:full", "menu:more"}))
async def menu_more(callback: CallbackQuery) -> None:
    from app.bot.utils.callbacks import safe_edit_message

    tg_id = callback.from_user.id if callback.from_user else 0
    await callback.answer()
    if callback.message:
        await safe_edit_message(
            callback.message,
            f"{ICON} <b>{BRAND}</b>\n"
            "<i>Справка и поддержка. Основные действия — на сводке.</i>",
            reply_markup=more_menu_keyboard(show_admin=_show_admin_menu(tg_id)),
        )


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(HELP_TEXT, reply_markup=main_menu_keyboard())


@router.callback_query(F.data == "menu:help")
async def menu_help(callback: CallbackQuery) -> None:
    from app.bot.utils.callbacks import safe_edit_message

    await callback.answer()
    if callback.message:
        await safe_edit_message(callback.message, HELP_TEXT, reply_markup=main_menu_keyboard())
