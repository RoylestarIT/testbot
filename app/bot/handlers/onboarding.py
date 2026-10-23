from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from app.core.config import get_settings
from app.db.models import User as DbUser
from app.db.repositories.user import UserRepository
from app.db.session import get_session_factory
from app.bot.keyboards.menu import main_menu_keyboard
from app.bot.ui import brand_title, muted, progress_bar

router = Router(name="onboarding")

STEPS = [
    brand_title("Шаг 1 из 3", tagline="Кабинет маркетплейса", icon="🏪")
    + "\n"
    + progress_bar(1, 3)
    + "\n\n"
    + muted("⚙️ Настройки → подключите 🟣 WB или 🔵 Ozon (API-ключ)."),
    brand_title("Шаг 2 из 3", tagline="Синхронизация", icon="🔄")
    + "\n"
    + progress_bar(2, 3)
    + "\n\n"
    + muted("🔄 Sync на сводке — подтянем новые отзывы в очередь."),
    brand_title("Шаг 3 из 3", tagline="Первый ответ", icon="✍️")
    + "\n"
    + progress_bar(3, 3)
    + "\n\n"
    + muted("📬 Очередь WB/Ozon или ручной ввод → 🎨 тон → варианты ответа."),
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
    rows = [action, [InlineKeyboardButton(text="➡️ Далее", callback_data=next_data)]]
    if step > 0:
        rows.append([InlineKeyboardButton(text="◀️ Назад", callback_data=f"onboarding:step:{step - 1}")])
    rows.append([InlineKeyboardButton(text="⏭ Пропустить", callback_data="onboarding:done")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


@router.callback_query(F.data == "menu:onboarding")
async def onboarding_start(callback: CallbackQuery) -> None:
    await callback.answer()
    if callback.message:
        await callback.message.edit_text(STEPS[0], reply_markup=_step_keyboard(0))


@router.callback_query(F.data.startswith("onboarding:step:"))
async def onboarding_step(callback: CallbackQuery) -> None:
    step = int(callback.data.split(":")[-1])
    step = max(0, min(step, 2))
    await callback.answer()
    if callback.message:
        await callback.message.edit_text(STEPS[step], reply_markup=_step_keyboard(step))


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
            "✨ <b>ReviewPilot</b>\n🎉 Настройка завершена.\n"
            "<i>Отзывы в Telegram: 3 варианта, правка, негатив — только вы.</i>",
            reply_markup=main_menu_keyboard(show_admin=tg_id in get_settings().admin_ids),
        )
