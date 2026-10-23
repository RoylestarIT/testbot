from __future__ import annotations

from typing import Any

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from loguru import logger

from app.bot.keyboards.menu import main_menu_keyboard
from app.bot.keyboards.reviews import (
    rating_keyboard,
    reviews_menu_keyboard,
    tone_keyboard,
    variants_keyboard,
)
from app.bot.states.review import ManualReviewStates
from app.core.config import get_settings
from app.db.models import ReviewStatus, User as DbUser
from app.db.repositories.reply import ReplyRepository
from app.db.repositories.review import ReviewRepository
from app.db.repositories.tone_profile import ToneProfileRepository
from app.db.session import get_session_factory
from app.services.generation_limit import can_generate, remaining_generations_today
from app.services.llm import LLMError, ToneProfileInput, generate_replies
from app.services.manual_review import get_or_create_manual_account, new_manual_external_id

router = Router(name="reviews")

REVIEWS_MENU_TEXT = (
    "<b>Отзывы</b>\n\n"
    "Lite-режим: введите текст отзыва вручную — бот предложит варианты ответа. "
    "Скопируйте понравившийся в кабинет маркетплейса."
)


def _examples_from_json(raw: Any) -> list[str] | None:
    if not raw:
        return None
    if isinstance(raw, list):
        return [str(item) for item in raw]
    return None


async def _tone_input(session, user_id: int, tone_key: str) -> ToneProfileInput:
    if tone_key == "default":
        return ToneProfileInput(description="Дружелюбный, профессиональный, лаконичный")
    profile = await ToneProfileRepository(session).get_by_id(int(tone_key))
    if profile is None or profile.user_id != user_id:
        return ToneProfileInput(description="Дружелюбный, профессиональный, лаконичный")
    return ToneProfileInput(
        description=profile.description,
        example_replies=_examples_from_json(profile.example_replies),
    )


def _format_variants_message(variants: list[str], selected_index: int, remaining: int | None) -> str:
    lines = ["<b>Варианты ответа</b>", ""]
    for index, text in enumerate(variants, start=1):
        marker = " 👈" if index - 1 == selected_index else ""
        lines.append(f"<b>{index}.</b> {text}{marker}")
    if remaining is not None:
        lines.extend(["", f"Осталось генераций сегодня (Lite): <b>{remaining}</b>"])
    return "\n".join(lines)


async def _ensure_review_record(
    *,
    user_id: int,
    review_text: str,
    rating: int,
    review_id: int | None,
) -> int:
    session_factory = get_session_factory()
    async with session_factory() as session:
        if review_id is not None:
            review = await ReviewRepository(session).get_by_id(review_id)
            if review is not None:
                return review.id
        account = await get_or_create_manual_account(session, user_id)
        review = await ReviewRepository(session).create(
            account_id=account.id,
            external_id=new_manual_external_id(),
            rating=rating,
            text=review_text,
            author="Покупатель (ручной ввод)",
            status=ReviewStatus.NEW,
            raw_json={"source": "manual", "rating": rating},
        )
        await session.commit()
        return review.id


async def _next_variant_index(session, review_id: int) -> int:
    replies = await ReplyRepository(session).list_by_review_id(review_id)
    if not replies:
        return 0
    return max(item.variant_index for item in replies) + 1


async def _generate_and_persist(
    *,
    user_id: int,
    review_text: str,
    rating: int,
    tone: ToneProfileInput,
    review_id: int | None,
) -> tuple[int, list[str]]:
    session_factory = get_session_factory()
    async with session_factory() as session:
        allowed, reason = await can_generate(session, user_id)
        if not allowed:
            raise LLMError(reason or "Лимит генераций исчерпан")

    review_id = await _ensure_review_record(
        user_id=user_id,
        review_text=review_text,
        rating=rating,
        review_id=review_id,
    )

    settings = get_settings()
    variants = await generate_replies(
        review_text,
        rating,
        tone,
        count=3,
        settings=settings,
    )

    async with session_factory() as session:
        start_index = await _next_variant_index(session, review_id)
        reply_repo = ReplyRepository(session)
        for offset, text in enumerate(variants):
            await reply_repo.create(
                review_id=review_id,
                variant_index=start_index + offset,
                text=text,
                model=settings.openai_model,
            )
        await session.commit()

    return review_id, variants


@router.callback_query(F.data == "menu:reviews")
async def menu_reviews(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.answer()
    if callback.message:
        await callback.message.edit_text(REVIEWS_MENU_TEXT, reply_markup=reviews_menu_keyboard())


@router.callback_query(F.data == "menu:main")
async def menu_main(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.answer()
    if callback.message:
        from app.bot.handlers.start import WELCOME_TEXT

        await callback.message.edit_text(WELCOME_TEXT, reply_markup=main_menu_keyboard())


@router.callback_query(F.data == "review:manual:start")
async def manual_start(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(ManualReviewStates.waiting_text)
    await callback.answer()
    if callback.message:
        await callback.message.edit_text(
            "Пришлите <b>текст отзыва</b> одним сообщением.",
        )


@router.callback_query(F.data == "review:cancel")
async def review_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.answer("Отменено")
    if callback.message:
        await callback.message.edit_text(REVIEWS_MENU_TEXT, reply_markup=reviews_menu_keyboard())


@router.message(ManualReviewStates.waiting_text, F.text)
async def manual_review_text(message: Message, state: FSMContext) -> None:
    text = (message.text or "").strip()
    if len(text) < 3:
        await message.answer("Текст слишком короткий. Напишите отзыв подробнее.")
        return
    await state.update_data(review_text=text)
    await state.set_state(ManualReviewStates.waiting_rating)
    await message.answer(
        "Выберите <b>оценку</b> (1–5 звёзд):",
        reply_markup=rating_keyboard(),
    )


@router.callback_query(ManualReviewStates.waiting_rating, F.data.startswith("review:rating:"))
async def manual_review_rating(callback: CallbackQuery, state: FSMContext, db_user: DbUser) -> None:
    rating = int(callback.data.split(":")[-1])
    await state.update_data(rating=rating)
    await state.set_state(ManualReviewStates.waiting_tone)

    session_factory = get_session_factory()
    async with session_factory() as session:
        profiles = await ToneProfileRepository(session).list_by_user_id(db_user.id)

    await callback.answer()
    if callback.message:
        await callback.message.edit_text(
            "Выберите <b>тон ответа</b>:",
            reply_markup=tone_keyboard(profiles),
        )


@router.callback_query(ManualReviewStates.waiting_tone, F.data.startswith("review:tone:"))
async def manual_review_tone(callback: CallbackQuery, state: FSMContext, db_user: DbUser) -> None:
    tone_key = callback.data.removeprefix("review:tone:")
    data = await state.get_data()
    review_text = data.get("review_text")
    rating = data.get("rating")
    if not review_text or rating is None:
        await state.clear()
        await callback.answer("Сессия сброшена. Начните заново.", show_alert=True)
        return

    await callback.answer("Генерирую варианты…")
    if callback.message:
        await callback.message.edit_text("⏳ Генерирую варианты ответа…")

    session_factory = get_session_factory()
    async with session_factory() as session:
        tone = await _tone_input(session, db_user.id, tone_key)

    try:
        review_id, variants = await _generate_and_persist(
            user_id=db_user.id,
            review_text=review_text,
            rating=int(rating),
            tone=tone,
            review_id=data.get("review_id"),
        )
    except LLMError as exc:
        logger.warning("LLM generation failed: {}", exc)
        if callback.message:
            await callback.message.edit_text(
                f"Не удалось сгенерировать ответы.\n\n{exc}",
                reply_markup=reviews_menu_keyboard(),
            )
        await state.clear()
        return

    await state.update_data(
        review_id=review_id,
        variants=variants,
        selected_index=0,
        tone_key=tone_key,
    )
    await state.set_state(ManualReviewStates.viewing_variants)

    async with session_factory() as session:
        remaining = await remaining_generations_today(session, db_user.id)

    if callback.message:
        await callback.message.edit_text(
            _format_variants_message(variants, 0, remaining),
            reply_markup=variants_keyboard(len(variants), 0),
        )


@router.callback_query(ManualReviewStates.viewing_variants, F.data.startswith("review:pick:"))
async def pick_variant(callback: CallbackQuery, state: FSMContext, db_user: DbUser) -> None:
    index = int(callback.data.split(":")[-1])
    data = await state.get_data()
    variants: list[str] = data.get("variants") or []
    if index < 0 or index >= len(variants):
        await callback.answer("Неверный вариант")
        return
    await state.update_data(selected_index=index)
    await callback.answer(f"Выбран вариант {index + 1}")

    session_factory = get_session_factory()
    async with session_factory() as session:
        remaining = await remaining_generations_today(session, db_user.id)

    if callback.message:
        await callback.message.edit_text(
            _format_variants_message(variants, index, remaining),
            reply_markup=variants_keyboard(len(variants), index),
        )


@router.callback_query(ManualReviewStates.viewing_variants, F.data == "review:publish")
async def publish_lite(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    variants: list[str] = data.get("variants") or []
    selected_index = int(data.get("selected_index", 0))
    review_id = data.get("review_id")
    if not variants:
        await callback.answer("Нет вариантов", show_alert=True)
        return

    text = variants[selected_index]
    await callback.answer("Скопируйте текст ниже")

    if review_id is not None:
        session_factory = get_session_factory()
        async with session_factory() as session:
            await ReviewRepository(session).update_status(int(review_id), ReviewStatus.PROCESSED)
            await session.commit()

    if callback.message:
        await callback.message.answer(
            "<b>Lite — скопируйте в кабинет маркетплейса:</b>\n\n"
            f"<code>{text}</code>",
            reply_markup=reviews_menu_keyboard(),
        )


@router.callback_query(F.data == "review:more")
async def more_variants(callback: CallbackQuery, state: FSMContext, db_user: DbUser) -> None:
    data = await state.get_data()
    review_text = data.get("review_text")
    rating = data.get("rating")
    tone_key = data.get("tone_key", "default")
    review_id = data.get("review_id")
    if not review_text or rating is None:
        await callback.answer("Начните с «Ответить на отзыв»", show_alert=True)
        return

    await callback.answer("Генерирую…")
    if callback.message:
        await callback.message.edit_text("⏳ Генерирую ещё варианты…")

    session_factory = get_session_factory()
    async with session_factory() as session:
        tone = await _tone_input(session, db_user.id, str(tone_key))

    try:
        review_id, variants = await _generate_and_persist(
            user_id=db_user.id,
            review_text=review_text,
            rating=int(rating),
            tone=tone,
            review_id=review_id,
        )
    except LLMError as exc:
        if callback.message:
            await callback.message.edit_text(
                f"Не удалось сгенерировать.\n\n{exc}",
                reply_markup=variants_keyboard(len(data.get("variants") or []), 0),
            )
        return

    await state.update_data(review_id=review_id, variants=variants, selected_index=0)
    await state.set_state(ManualReviewStates.viewing_variants)

    async with session_factory() as session:
        remaining = await remaining_generations_today(session, db_user.id)

    if callback.message:
        await callback.message.edit_text(
            _format_variants_message(variants, 0, remaining),
            reply_markup=variants_keyboard(len(variants), 0),
        )


@router.callback_query(F.data == "review:change_tone")
async def change_tone(callback: CallbackQuery, state: FSMContext, db_user: DbUser) -> None:
    await state.set_state(ManualReviewStates.waiting_tone)
    session_factory = get_session_factory()
    async with session_factory() as session:
        profiles = await ToneProfileRepository(session).list_by_user_id(db_user.id)
    await callback.answer()
    if callback.message:
        await callback.message.edit_text(
            "Выберите другой <b>тон ответа</b>:",
            reply_markup=tone_keyboard(profiles),
        )
