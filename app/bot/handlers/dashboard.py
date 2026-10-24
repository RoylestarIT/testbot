from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from app.bot.copy import differentiators_section
from app.bot.marketing import feature_roadmap_text, for_whom_text, market_compare_text
from app.bot.keyboards.menu import dashboard_keyboard, main_menu_keyboard
from app.bot.keyboards.positioning import positioning_keyboard
from app.bot.utils.callbacks import safe_edit_message
from app.bot.product_news import product_news_version, user_should_see_product_news
from app.core.config import get_settings
from app.db.models import User as DbUser
from app.db.repositories.user import UserRepository
from app.db.session import get_session_factory
from app.services.dashboard import build_user_dashboard
from app.services.dashboard_details import build_dashboard_details
from app.services.pro_access import activate_trial_pro, has_paid_pro

router = Router(name="dashboard")


def _show_admin(tg_id: int) -> bool:
    return tg_id in get_settings().admin_ids


async def _dashboard_ui(session, db_user: DbUser, tg_id: int) -> tuple[str, object] | None:
    user = await UserRepository(session).get_by_id(db_user.id)
    if user is None:
        return None
    text = await build_user_dashboard(session, user)
    paid_pro = await has_paid_pro(session, user.id)
    settings = get_settings()
    kb = dashboard_keyboard(
        show_trial=not user.trial_pro_used and not paid_pro,
        show_onboarding=user.onboarding_completed_at is None,
        show_admin=_show_admin(tg_id),
        show_product_news=user_should_see_product_news(user, settings),
    )
    return text, kb


async def _send_dashboard(target: Message, db_user: DbUser) -> None:
    session_factory = get_session_factory()
    async with session_factory() as session:
        ui = await _dashboard_ui(session, db_user, target.from_user.id if target.from_user else 0)
    if ui is None:
        await target.answer("Ошибка профиля.")
        return
    text, kb = ui
    await target.answer(text, reply_markup=kb)


async def _edit_dashboard(message: Message, db_user: DbUser) -> None:
    session_factory = get_session_factory()
    async with session_factory() as session:
        ui = await _dashboard_ui(session, db_user, message.from_user.id if message.from_user else 0)
    if ui is None:
        return
    text, kb = ui
    await safe_edit_message(message, text, reply_markup=kb)


@router.message(Command("dashboard"))
async def cmd_dashboard(message: Message, db_user: DbUser) -> None:
    await _send_dashboard(message, db_user)


@router.callback_query(F.data == "news:dismiss")
async def news_dismiss(callback: CallbackQuery, db_user: DbUser) -> None:
    settings = get_settings()
    version = product_news_version(settings)
    if not version:
        await callback.answer()
        return
    session_factory = get_session_factory()
    async with session_factory() as session:
        await UserRepository(session).set_product_news_seen(db_user.id, version)
        await session.commit()
    await callback.answer("Скрыли обновления")
    if callback.message:
        await _edit_dashboard(callback.message, db_user)


@router.callback_query(F.data == "menu:dashboard")
async def menu_dashboard(callback: CallbackQuery, db_user: DbUser) -> None:
    await callback.answer()
    if callback.message:
        await _edit_dashboard(callback.message, db_user)


@router.callback_query(F.data == "menu:why_us")
async def menu_why_us(callback: CallbackQuery) -> None:
    await callback.answer()
    text = differentiators_section(compact=False)
    if callback.message:
        await safe_edit_message(callback.message, text, reply_markup=positioning_keyboard())


@router.callback_query(F.data == "menu:market_compare")
async def menu_market_compare(callback: CallbackQuery) -> None:
    await callback.answer()
    if callback.message:
        await safe_edit_message(
            callback.message,
            market_compare_text(),
            reply_markup=positioning_keyboard(back="menu:why_us"),
        )


@router.callback_query(F.data == "menu:for_whom")
async def menu_for_whom(callback: CallbackQuery) -> None:
    await callback.answer()
    if callback.message:
        await safe_edit_message(
            callback.message,
            for_whom_text(),
            reply_markup=positioning_keyboard(back="menu:why_us"),
        )


@router.callback_query(F.data == "menu:roadmap")
async def menu_roadmap(callback: CallbackQuery) -> None:
    await callback.answer()
    if callback.message:
        await safe_edit_message(
            callback.message,
            feature_roadmap_text(),
            reply_markup=positioning_keyboard(back="menu:why_us"),
        )


@router.callback_query(F.data == "menu:dashboard:details")
async def menu_dashboard_details(callback: CallbackQuery, db_user: DbUser) -> None:
    session_factory = get_session_factory()
    async with session_factory() as session:
        user = await UserRepository(session).get_by_id(db_user.id)
        if user is None:
            await callback.answer("Ошибка")
            return
        text = await build_dashboard_details(session, user)
    await callback.answer()
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🏠  Сводка", callback_data="menu:dashboard")],
        ]
    )
    if callback.message:
        await safe_edit_message(callback.message, text, reply_markup=kb)


@router.callback_query(F.data == "menu:trial_pro")
async def activate_trial(callback: CallbackQuery, db_user: DbUser) -> None:
    session_factory = get_session_factory()
    async with session_factory() as session:
        user, err = await activate_trial_pro(session, db_user.id)
        await session.commit()
    if err:
        await callback.answer(err, show_alert=True)
        return
    settings = get_settings()
    await callback.answer("Trial PRO активирован!")
    if callback.message and user and user.trial_pro_until:
        await safe_edit_message(
            callback.message,
            f"🎁 Trial PRO на <b>{settings.trial_pro_days}</b> дней до "
            f"<b>{user.trial_pro_until.strftime('%d.%m.%Y')}</b>.\n"
            f"Бесплатных publish: <b>{user.free_api_publishes_remaining}</b>",
            reply_markup=main_menu_keyboard(
                show_admin=_show_admin(callback.from_user.id if callback.from_user else 0)
            ),
        )
