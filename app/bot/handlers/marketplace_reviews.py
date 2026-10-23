from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from loguru import logger

from app.bot.handlers.reviews import (
    REVIEWS_MENU_TEXT,
    _format_variants_message,
    _generate_and_persist,
    _tone_input,
)
from app.bot.keyboards.reviews import reviews_menu_keyboard, tone_keyboard, variants_keyboard
from app.bot.filters.mp_flow import MpFlowFilter
from app.bot.states.marketplace_review import MarketplaceReviewStates
from app.bot.states.review import ManualReviewStates
from app.db.models import Marketplace, ReviewStatus, User as DbUser
from app.db.repositories.account import AccountRepository
from app.db.repositories.review import ReviewRepository
from app.db.repositories.tone_profile import ToneProfileRepository
from app.db.session import get_session_factory
from app.services.generation_limit import remaining_generations_today
from app.services.llm import LLMError
from app.services.marketplace.base import MarketplaceAPIError
from app.services.marketplace.publish_service import publish_reply_to_marketplace
from app.services.marketplace.sync_service import sync_account_reviews

router = Router(name="marketplace_reviews")


def _mp_reviews_keyboard(reviews: list, page: int = 0) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for review in reviews[:10]:
        preview = (review.text or "—")[:40].replace("\n", " ")
        rating = f"⭐{review.rating}" if review.rating else "⭐?"
        rows.append(
            [
                InlineKeyboardButton(
                    text=f"{rating} {preview}",
                    callback_data=f"review:mp:pick:{review.id}",
                )
            ]
        )
    rows.append([InlineKeyboardButton(text="← Отзывы", callback_data="menu:reviews")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _publish_confirm_keyboard(review_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Опубликовать на маркетплейс",
                    callback_data=f"review:mp:confirm:{review_id}",
                )
            ],
            [InlineKeyboardButton(text="Отмена", callback_data="review:mp:cancel_publish")],
        ]
    )


@router.callback_query(F.data == "review:sync")
async def sync_reviews(callback: CallbackQuery, db_user: DbUser) -> None:
    await callback.answer("Синхронизация…")
    session_factory = get_session_factory()
    total_new = 0
    errors: list[str] = []
    async with session_factory() as session:
        accounts = await AccountRepository(session).list_by_user_id(db_user.id, active_only=True)
        mp_accounts = [a for a in accounts if a.marketplace in (Marketplace.WB, Marketplace.OZON)]
        for account in mp_accounts:
            try:
                created, _ = await sync_account_reviews(session, account)
                total_new += created
            except MarketplaceAPIError as exc:
                logger.warning("Sync failed account_id={} err={}", account.id, exc)
                errors.append(str(exc))
        await session.commit()

    lines = [f"Синхронизация завершена. Новых отзывов: <b>{total_new}</b>."]
    if errors:
        lines.append("\nОшибки:\n" + "\n".join(f"• {e}" for e in errors[:3]))
    if callback.message:
        await callback.message.edit_text("\n".join(lines), reply_markup=reviews_menu_keyboard())


@router.callback_query(F.data == "review:mp:list")
async def list_mp_reviews(callback: CallbackQuery, db_user: DbUser) -> None:
    session_factory = get_session_factory()
    async with session_factory() as session:
        accounts = await AccountRepository(session).list_by_user_id(db_user.id, active_only=True)
        mp_ids = [a.id for a in accounts if a.marketplace in (Marketplace.WB, Marketplace.OZON)]
        reviews: list = []
        for acc_id in mp_ids:
            reviews.extend(
                await ReviewRepository(session).list_by_account(
                    acc_id,
                    status=ReviewStatus.NEW,
                    limit=20,
                )
            )
    reviews.sort(key=lambda r: r.created_at, reverse=True)
    await callback.answer()
    if not reviews:
        text = "Нет новых отзывов из API. Нажмите «Синхронизировать отзывы» или подключите кабинет в Настройках."
    else:
        text = "<b>Новые отзывы из маркетплейсов</b>\n\nВыберите отзыв для ответа:"
    if callback.message:
        await callback.message.edit_text(
            text,
            reply_markup=_mp_reviews_keyboard(reviews) if reviews else reviews_menu_keyboard(),
        )


@router.callback_query(F.data.startswith("review:mp:pick:"))
async def mp_pick_review(callback: CallbackQuery, state: FSMContext, db_user: DbUser) -> None:
    review_id = int(callback.data.split(":")[-1])
    session_factory = get_session_factory()
    async with session_factory() as session:
        review = await ReviewRepository(session).get_by_id(review_id)
        if review is None:
            await callback.answer("Отзыв не найден", show_alert=True)
            return
        account = await AccountRepository(session).get_by_id(review.account_id)
        if account is None or account.user_id != db_user.id:
            await callback.answer("Нет доступа", show_alert=True)
            return
        profiles = await ToneProfileRepository(session).list_by_user_id(db_user.id)

    await state.update_data(
        review_id=review_id,
        review_text=review.text or "",
        rating=review.rating or 5,
        mp_flow=True,
    )
    await state.set_state(ManualReviewStates.waiting_tone)
    await callback.answer()
    if callback.message:
        preview = (review.text or "—")[:500]
        await callback.message.edit_text(
            f"<b>Отзыв</b>\n{preview}\n\nВыберите <b>тон ответа</b>:",
            reply_markup=tone_keyboard(profiles),
        )


@router.callback_query(
    ManualReviewStates.waiting_tone,
    F.data.startswith("review:tone:"),
    MpFlowFilter(),
)
async def mp_tone_generate(callback: CallbackQuery, state: FSMContext, db_user: DbUser) -> None:
    tone_key = callback.data.removeprefix("review:tone:")
    data = await state.get_data()
    review_text = data.get("review_text")
    rating = data.get("rating")
    review_id = data.get("review_id")
    if not review_text or rating is None:
        await state.clear()
        await callback.answer("Сессия сброшена", show_alert=True)
        return

    await callback.answer("Генерирую…")
    if callback.message:
        await callback.message.edit_text("⏳ Генерирую варианты…")

    session_factory = get_session_factory()
    async with session_factory() as session:
        tone = await _tone_input(session, db_user.id, tone_key)

    try:
        review_id, variants = await _generate_and_persist(
            user_id=db_user.id,
            review_text=str(review_text),
            rating=int(rating),
            tone=tone,
            review_id=int(review_id) if review_id else None,
        )
    except LLMError as exc:
        if callback.message:
            await callback.message.edit_text(f"Ошибка генерации:\n{exc}", reply_markup=reviews_menu_keyboard())
        await state.clear()
        return

    await state.update_data(
        review_id=review_id,
        variants=variants,
        selected_index=0,
        tone_key=tone_key,
        mp_flow=True,
    )
    await state.set_state(MarketplaceReviewStates.viewing_variants)

    async with session_factory() as session:
        remaining = await remaining_generations_today(session, db_user.id)

    if callback.message:
        await callback.message.edit_text(
            _format_variants_message(variants, 0, remaining),
            reply_markup=_mp_variants_keyboard(variants, 0, review_id),
        )


def _mp_variants_keyboard(variants: list[str], selected: int, review_id: int) -> InlineKeyboardMarkup:
    base = variants_keyboard(len(variants), selected)
    extra = [
        [
            InlineKeyboardButton(
                text="Опубликовать на WB/Ozon",
                callback_data=f"review:mp:publish:{review_id}",
            )
        ],
        [InlineKeyboardButton(text="← Новые отзывы", callback_data="review:mp:list")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=base.inline_keyboard[:-1] + extra)


@router.callback_query(
    MarketplaceReviewStates.viewing_variants,
    F.data.startswith("review:pick:"),
    MpFlowFilter(),
)
async def mp_pick_variant(callback: CallbackQuery, state: FSMContext, db_user: DbUser) -> None:
    data = await state.get_data()
    index = int(callback.data.split(":")[-1])
    variants: list[str] = data.get("variants") or []
    review_id = int(data.get("review_id", 0))
    if index < 0 or index >= len(variants):
        await callback.answer("Неверный вариант")
        return
    await state.update_data(selected_index=index)
    await callback.answer(f"Вариант {index + 1}")

    session_factory = get_session_factory()
    async with session_factory() as session:
        remaining = await remaining_generations_today(session, db_user.id)

    if callback.message:
        await callback.message.edit_text(
            _format_variants_message(variants, index, remaining),
            reply_markup=_mp_variants_keyboard(variants, index, review_id),
        )


@router.callback_query(F.data.startswith("review:mp:publish:"))
async def mp_publish_ask_confirm(callback: CallbackQuery, state: FSMContext) -> None:
    review_id = int(callback.data.split(":")[-1])
    data = await state.get_data()
    variants: list[str] = data.get("variants") or []
    selected = int(data.get("selected_index", 0))
    if not variants:
        await callback.answer("Сначала сгенерируйте варианты", show_alert=True)
        return
    text = variants[selected]
    await state.update_data(publish_text=text, publish_review_id=review_id)
    await state.set_state(MarketplaceReviewStates.awaiting_publish_confirm)
    await callback.answer()
    if callback.message:
        await callback.message.edit_text(
            "<b>Подтвердите публикацию</b>\n\n"
            f"<code>{text}</code>",
            reply_markup=_publish_confirm_keyboard(review_id),
        )


@router.callback_query(MarketplaceReviewStates.awaiting_publish_confirm, F.data.startswith("review:mp:confirm:"))
async def mp_publish_confirm(callback: CallbackQuery, state: FSMContext, db_user: DbUser) -> None:
    data = await state.get_data()
    text = data.get("publish_text")
    review_id = data.get("publish_review_id")
    if not text or review_id is None:
        await callback.answer("Данные устарели", show_alert=True)
        await state.clear()
        return

    await callback.answer("Публикую…")
    session_factory = get_session_factory()
    try:
        async with session_factory() as session:
            review = await ReviewRepository(session).get_by_id(int(review_id))
            if review is None:
                raise MarketplaceAPIError("Отзыв не найден")
            account = await AccountRepository(session).get_by_id(review.account_id)
            if account is None or account.user_id != db_user.id:
                raise MarketplaceAPIError("Нет доступа к кабинету")
            await publish_reply_to_marketplace(session, review, str(text))
            await session.commit()
    except MarketplaceAPIError as exc:
        logger.warning("User publish failed review_id={} err={}", review_id, exc)
        if callback.message:
            await callback.message.edit_text(
                f"Не удалось опубликовать:\n\n{exc}",
                reply_markup=reviews_menu_keyboard(),
            )
        await state.clear()
        return

    await state.clear()
    if callback.message:
        await callback.message.edit_text(
            "✅ Ответ опубликован на маркетплейсе.",
            reply_markup=reviews_menu_keyboard(),
        )


@router.callback_query(F.data == "review:mp:cancel_publish")
async def mp_publish_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(MarketplaceReviewStates.viewing_variants)
    await callback.answer("Отменено")
    data = await state.get_data()
    variants: list[str] = data.get("variants") or []
    review_id = int(data.get("review_id", 0))
    selected = int(data.get("selected_index", 0))
    if callback.message and variants:
        await callback.message.edit_text(
            _format_variants_message(variants, selected, None),
            reply_markup=_mp_variants_keyboard(variants, selected, review_id),
        )
