from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from app.bot.states.support import SupportContactStates
from app.bot.support_ui import support_keyboard, support_screen_text
from app.core.config import get_settings
from app.db.models import User as DbUser
from app.db.repositories.user import UserRepository
from app.db.session import get_session_factory
from app.services.support_context import build_support_user_card

router = Router(name="support")


@router.callback_query(F.data == "menu:support")
async def menu_support(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.answer()
    if callback.message:
        await callback.message.edit_text(support_screen_text(), reply_markup=support_keyboard())


@router.callback_query(F.data == "support:write")
async def support_write_start(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(SupportContactStates.waiting_message)
    await callback.answer()
    if callback.message:
        await callback.message.edit_text(
            support_screen_text()
            + "\n\n<b>Опишите проблему одним сообщением</b> — мы перешлём её администратору с вашим профилем.",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="◀️ Отмена", callback_data="menu:support")],
                ]
            ),
        )


@router.message(SupportContactStates.waiting_message, F.text)
async def support_message_received(message: Message, state: FSMContext, db_user: DbUser, bot: Bot) -> None:
    text = (message.text or "").strip()
    if len(text) < 5:
        await message.answer("Слишком коротко — опишите проблему подробнее.")
        return

    settings = get_settings()
    session_factory = get_session_factory()
    async with session_factory() as session:
        user = await UserRepository(session).get_by_id(db_user.id)
        if user is None:
            await message.answer("Ошибка профиля.")
            await state.clear()
            return
        card = await build_support_user_card(session, user)

    admin_text = f"{card}\n\n<b>Сообщение:</b>\n{text}"
    delivered = False
    for admin_id in settings.admin_ids:
        try:
            await bot.send_message(admin_id, admin_text)
            delivered = True
        except Exception:
            continue

    await state.clear()
    if delivered:
        await message.answer(
            "✅ Сообщение отправлено в поддержку.\n"
            "Обычно отвечаем в Telegram в рабочие часы.",
            reply_markup=support_keyboard(),
        )
    else:
        await message.answer(
            "Не удалось доставить сообщение администратору. "
            "Напишите напрямую через кнопку «Написать в поддержку».",
            reply_markup=support_keyboard(),
        )
