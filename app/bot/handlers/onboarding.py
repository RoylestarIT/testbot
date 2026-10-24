from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from app.core.config import get_settings
from app.db.models import User as DbUser
from app.db.repositories.user import UserRepository
from app.db.session import get_session_factory
from app.bot.ui import BRAND, ICON, brand_title, muted, progress_bar
from app.services.onboarding_checklist import onboarding_is_complete

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
    + muted("📬 «Ответы на отзывы» → 🎨 тон → варианты → отправить."),
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
        action = [InlineKeyboardButton(text="📬 Ответы на отзывы", callback_data="review:mp:list")]
    rows = [action, [InlineKeyboardButton(text="➡️ Далее", callback_data=next_data)]]
    if step > 0:
        rows.append([InlineKeyboardButton(text="◀️ Назад", callback_data=f"onboarding:step:{step - 1}")])
    rows.append([InlineKeyboardButton(text="⏭ К сводке", callback_data="onboarding:skip")])
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


@router.callback_query(F.data == "onboarding:skip")
async def onboarding_skip(callback: CallbackQuery) -> None:
    await callback.answer()
    if callback.message:
        await callback.message.edit_text(
            f"{ICON} <b>{BRAND}</b>\n"
            "Чеклист быстрого старта остаётся на сводке — вернитесь, когда будет время.",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="🏠 Сводка", callback_data="menu:dashboard")],
                ]
            ),
        )


@router.callback_query(F.data == "onboarding:done")
async def onboarding_done(callback: CallbackQuery, db_user: DbUser) -> None:
    session_factory = get_session_factory()
    async with session_factory() as session:
        user = await UserRepository(session).get_by_id(db_user.id)
        if user is None:
            await callback.answer("Ошибка профиля", show_alert=True)
            return
        if not await onboarding_is_complete(session, user):
            await callback.answer(
                "Сначала выполните шаги чеклиста (кабинет, тон, первый ответ).",
                show_alert=True,
            )
            return
        await UserRepository(session).complete_onboarding(db_user.id)
        await session.commit()
    await callback.answer("Готово!")
    tg_id = callback.from_user.id if callback.from_user else 0
    rows = [
        [InlineKeyboardButton(text="📬 Ответы на отзывы", callback_data="review:mp:list")],
        [InlineKeyboardButton(text="💎 Тарифы", callback_data="menu:subscription")],
        [InlineKeyboardButton(text="🏠 Сводка", callback_data="menu:dashboard")],
    ]
    if callback.message:
        await callback.message.edit_text(
            f"{ICON} <b>{BRAND}</b>\n🎉 Настройка завершена.\n"
            "<i>Отзывы в Telegram: 3 варианта, правка, негатив — только вы.</i>",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=rows),
        )
