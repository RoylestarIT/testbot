from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from app.bot.keyboards.menu import main_menu_keyboard, dashboard_keyboard
from app.core.config import get_settings
from app.db.models import User as DbUser
from app.db.repositories.user import UserRepository
from app.db.session import get_session_factory
from app.services.dashboard import build_user_dashboard
from app.services.pro_access import activate_trial_pro, has_paid_pro

router = Router(name="dashboard")


def _show_admin(tg_id: int) -> bool:
    return tg_id in get_settings().admin_ids


async def _send_dashboard(target: Message, db_user: DbUser) -> None:
    session_factory = get_session_factory()
    async with session_factory() as session:
        user = await UserRepository(session).get_by_id(db_user.id)
        if user is None:
            await target.answer("Ошибка профиля.")
            return
        text = await build_user_dashboard(session, user)
        paid_pro = await has_paid_pro(session, user.id)
        show_trial = not user.trial_pro_used and not paid_pro
        show_onboarding = user.onboarding_completed_at is None
    await target.answer(
        text,
        reply_markup=dashboard_keyboard(
            show_trial=show_trial,
            show_onboarding=show_onboarding,
            show_admin=_show_admin(target.from_user.id if target.from_user else 0),
        ),
    )


@router.message(Command("dashboard"))
async def cmd_dashboard(message: Message, db_user: DbUser) -> None:
    await _send_dashboard(message, db_user)


@router.callback_query(F.data == "menu:dashboard")
async def menu_dashboard(callback: CallbackQuery, db_user: DbUser) -> None:
    await callback.answer()
    if callback.message:
        session_factory = get_session_factory()
        async with session_factory() as session:
            user = await UserRepository(session).get_by_id(db_user.id)
            if user is None:
                return
            text = await build_user_dashboard(session, user)
            paid_pro = await has_paid_pro(session, user.id)
            show_trial = not user.trial_pro_used and not paid_pro
            show_onboarding = user.onboarding_completed_at is None
        await callback.message.edit_text(
            text,
            reply_markup=dashboard_keyboard(
                show_trial=show_trial,
                show_onboarding=show_onboarding,
                show_admin=_show_admin(callback.from_user.id if callback.from_user else 0),
            ),
        )


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
        await callback.message.answer(
            f"🎁 Trial PRO на <b>{settings.trial_pro_days}</b> дней до "
            f"<b>{user.trial_pro_until.strftime('%d.%m.%Y')}</b>.\n"
            f"Бесплатных publish: <b>{user.free_api_publishes_remaining}</b>",
            reply_markup=main_menu_keyboard(show_admin=_show_admin(callback.from_user.id if callback.from_user else 0)),
        )
