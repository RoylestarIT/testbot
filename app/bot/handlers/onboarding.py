from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from app.core.config import get_settings
from app.db.models import User as DbUser
from app.db.repositories.user import UserRepository
from app.db.session import get_session_factory
from app.bot.keyboards.menu import main_menu_keyboard

router = Router(name="onboarding")

STEPS = [
    (
        "1/3 · <b>Кабинет маркетплейса</b>\n\n"
        "Откройте «Настройки» → подключите WB или Ozon (API-ключ)."
    ),
    (
        "2/3 · <b>Синхронизация</b>\n\n"
        "«Отзывы» → «Синхронизировать отзывы» — подтянем новые отзывы в бот."
    ),
    (
        "3/3 · <b>Первый ответ</b>\n\n"
        "«Новые из маркетплейсов» или ручной ввод → выберите тон → получите варианты."
    ),
]


def _step_keyboard(step: int) -> InlineKeyboardMarkup:
    if step == 0:
        next_data = "onboarding:step:1"
        action = [InlineKeyboardButton(text="⚙️ Открыть настройки", callback_data="menu:settings")]
    elif step == 1:
        next_data = "onboarding:step:2"
        action = [InlineKeyboardButton(text="🔄 Синхронизировать", callback_data="review:sync")]
    else:
        next_data = "onboarding:done"
        action = [InlineKeyboardButton(text="📬 Новые отзывы", callback_data="review:mp:list")]
    rows = [action, [InlineKeyboardButton(text="Далее →", callback_data=next_data)]]
    if step > 0:
        rows.append([InlineKeyboardButton(text="← Назад", callback_data=f"onboarding:step:{step - 1}")])
    rows.append([InlineKeyboardButton(text="Пропустить", callback_data="onboarding:done")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


@router.callback_query(F.data == "menu:onboarding")
async def onboarding_start(callback: CallbackQuery) -> None:
    await callback.answer()
    if callback.message:
        await callback.message.edit_text(
            "🚀 <b>Быстрый старт</b>\n\n" + STEPS[0],
            reply_markup=_step_keyboard(0),
        )


@router.callback_query(F.data.startswith("onboarding:step:"))
async def onboarding_step(callback: CallbackQuery) -> None:
    step = int(callback.data.split(":")[-1])
    step = max(0, min(step, 2))
    await callback.answer()
    if callback.message:
        await callback.message.edit_text(
            f"🚀 <b>Быстрый старт</b>\n\n{STEPS[step]}",
            reply_markup=_step_keyboard(step),
        )


@router.callback_query(F.data == "onboarding:done")
async def onboarding_done(callback: CallbackQuery, db_user: DbUser) -> None:
    session_factory = get_session_factory()
    async with session_factory() as session:
        await UserRepository(session).complete_onboarding(db_user.id)
        await session.commit()
    await callback.answer("Готово!")
    tg_id = callback.from_user.id if callback.from_user else 0
    if callback.message:
        await callback.message.edit_text(
            "✅ Настройка завершена. Удачных продаж!",
            reply_markup=main_menu_keyboard(show_admin=tg_id in get_settings().admin_ids),
        )
