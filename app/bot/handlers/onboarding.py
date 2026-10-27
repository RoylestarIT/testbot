from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from app.bot.ui import BRAND, ICON, brand_title, muted, progress_bar
from app.bot.utils.callbacks import safe_edit_message
from app.db.models import User as DbUser
from app.db.repositories.user import UserRepository
from app.db.session import get_session_factory
from app.services.onboarding_checklist import (
    onboarding_is_complete,
    onboarding_step_states,
    try_complete_onboarding,
)

router = Router(name="onboarding")

_STEP_META = [
    ("Кабинет WB/Ozon", "⚙️ Настройки → подключите ключ кабинета.", "menu:settings"),
    ("Обновление отзывов", "🔄 На сводке — «Обновить», подтянуть отзывы.", "review:sync"),
    ("Тон ответа", "⚙️ Настройки → «Тон ответа» — как звучат ваши ответы.", "settings:tone"),
]


def _step_body(step: int, states: list[tuple[str, bool]]) -> str:
    total = len(states)
    step = max(0, min(step, total - 1))
    done_count = sum(1 for _, ok in states if ok)
    lines = [
        brand_title(f"Шаг {step + 1} из {total}", tagline="Быстрый старт", icon="🚀"),
        progress_bar(step + 1, total),
        "",
    ]
    for i, (label, ok) in enumerate(states):
        mark = "✅" if ok else ("👉" if i == step else "⬜")
        lines.append(f"{mark}  {label}")
    lines.append("")
    title, hint, _ = _STEP_META[step]
    lines.append(f"<b>{title}</b>")
    lines.append(muted(hint))
    if done_count == total:
        lines.append("")
        lines.append(muted("Все шаги выполнены — нажмите «Завершить»."))
    return "\n".join(lines)


def _step_keyboard(step: int, states: list[tuple[str, bool]]) -> InlineKeyboardMarkup:
    total = len(states)
    step = max(0, min(step, total - 1))
    _, _, action_cb = _STEP_META[step]
    all_done = all(ok for _, ok in states)
    rows: list[list[InlineKeyboardButton]] = [
        [InlineKeyboardButton(text="▶️ Перейти к шагу", callback_data=action_cb)],
    ]
    nav: list[InlineKeyboardButton] = []
    if step > 0:
        nav.append(InlineKeyboardButton(text="◀️ Назад", callback_data=f"onboarding:step:{step - 1}"))
    if step < total - 1:
        nav.append(InlineKeyboardButton(text="➡️ Далее", callback_data=f"onboarding:step:{step + 1}"))
    if nav:
        rows.append(nav)
    if all_done:
        rows.insert(0, [InlineKeyboardButton(text="✅ Завершить настройку", callback_data="onboarding:done")])
    rows.append([InlineKeyboardButton(text="⏭ К сводке", callback_data="onboarding:skip")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def onboarding_finished_screen() -> tuple[str, InlineKeyboardMarkup]:
    return _onboarding_complete_text(), _onboarding_complete_keyboard()


def _onboarding_complete_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📬 Ответы на отзывы", callback_data="review:mp:list")],
            [InlineKeyboardButton(text="💎 Тарифы", callback_data="menu:subscription")],
            [InlineKeyboardButton(text="🏠 Сводка", callback_data="menu:dashboard")],
        ]
    )


def _onboarding_complete_text() -> str:
    return (
        f"{ICON} <b>{BRAND}</b>\n🎉 Подключение завершено (3 из 3).\n"
        "<i>Отзывы в Telegram: 3 варианта, правка, негатив — только вы.</i>"
    )


async def _show_onboarding_complete(callback: CallbackQuery) -> None:
    if callback.message:
        await safe_edit_message(
            callback.message,
            _onboarding_complete_text(),
            reply_markup=_onboarding_complete_keyboard(),
        )


def _first_incomplete_step(states: list[tuple[str, bool]]) -> int:
    for i, (_, ok) in enumerate(states):
        if not ok:
            return i
    return max(0, len(states) - 1)


async def _render_onboarding(callback: CallbackQuery, db_user: DbUser, step: int | None = None) -> None:
    if callback.message is None:
        return
    session_factory = get_session_factory()
    async with session_factory() as session:
        user = await UserRepository(session).get_by_id(db_user.id)
        if user is None:
            return
        states = await onboarding_step_states(session, user)
        if await try_complete_onboarding(session, user):
            await session.commit()
            await _show_onboarding_complete(callback)
            return
    if step is None:
        step = _first_incomplete_step(states)
    text = _step_body(step, states)
    await safe_edit_message(callback.message, text, reply_markup=_step_keyboard(step, states))


@router.callback_query(F.data == "menu:onboarding")
async def onboarding_start(callback: CallbackQuery, db_user: DbUser) -> None:
    await callback.answer()
    await _render_onboarding(callback, db_user)


@router.callback_query(F.data.startswith("onboarding:step:"))
async def onboarding_step(callback: CallbackQuery, db_user: DbUser) -> None:
    step = int(callback.data.split(":")[-1])
    await callback.answer()
    await _render_onboarding(callback, db_user, step=step)


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
                "Сначала выполните 3 шага: кабинет, обновление отзывов и тон ответа.",
                show_alert=True,
            )
            return
        await UserRepository(session).complete_onboarding(db_user.id)
        await session.commit()
    await callback.answer("Готово!")
    await _show_onboarding_complete(callback)
