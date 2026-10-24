from __future__ import annotations

from datetime import UTC, datetime, timedelta

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from app.bot.handlers.reviews import QUICK_REPLY_TEMPLATES, _build_variants_keyboard
from app.bot.keyboards.empty_states import no_cabinets_keyboard, no_new_reviews_keyboard
from app.bot.utils.callbacks import safe_edit_message
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from loguru import logger

from app.bot.copy import (
    COPY_HINT,
    MP_LIST_EMPTY,
    MP_LIST_HEADER,
    MP_NO_CABINETS,
    NEGATIVE_PUBLISH_WARN,
    PRO_PUBLISH_REQUIRED,
    PUBLISH_SUCCESS,
    SYNC_DONE,
    SYNC_INTRO,
    Ozon_FORBIDDEN_HINT,
)
from app.bot.filters.mp_flow import MpFlowFilter
from app.bot.handlers.reviews import (
    _format_variants_message,
    _generate_and_persist,
    _tone_input,
)
from app.bot.keyboards.nav import after_review_action_keyboard, nav_home_queue
from app.bot.keyboards.reviews import reviews_menu_keyboard, reviews_queue_toolbar, tone_keyboard, variants_keyboard
from app.bot.ui import REVIEWS_HUB_BUTTON
from app.bot.keyboards.settings import sync_accounts_keyboard
from app.bot.states.marketplace_review import MarketplaceReviewStates
from app.bot.states.review import ManualReviewStates
from app.db.models import Marketplace, ReviewStatus, User as DbUser
from app.db.repositories.account import AccountRepository
from app.db.repositories.review import ReviewRepository
from app.db.repositories.tone_profile import ToneProfileRepository
from app.db.session import get_session_factory
from app.services.generation_limit import remaining_generations_today
from app.services.pro_access import can_api_publish
from app.services.llm import LLMError
from app.services.marketplace.base import MarketplaceAPIError
from app.services.marketplace.publish_service import publish_reply_to_marketplace
from app.services.marketplace.review_format import format_review_card
from app.bot.utils.reply_checks import validate_reply_for_user
from app.core.config import get_settings
from app.db.repositories.reply import ReplyRepository
from app.services.bulk_quick_reply import (
    apply_bulk_template,
    apply_bulk_template_with_publish,
    list_bulk_eligible,
)
from app.services.generation_limit import is_pro_user
from app.services.conversion_upsell import first_reply_upsell_suffix
from app.services.marketplace.auto_publish import try_auto_publish_review
from app.services.marketplace.sync_service import sync_account_reviews
from app.tasks.poller import format_ui_time

router = Router(name="marketplace_reviews")

MP_LIST_PAGE_SIZE = 10


async def _persist_selected_reply(
    session,
    review_id: int,
    text: str,
    *,
    selected_index: int,
) -> None:
    await ReplyRepository(session).create(
        review_id=review_id,
        variant_index=100 + selected_index,
        text=text,
        model="user_edit",
    )


async def _queue_has_next(state: FSMContext, review_id: int | None) -> bool:
    if review_id is None:
        return False
    data = await state.get_data()
    queue = [int(x) for x in (data.get("mp_queue") or [])]
    if review_id not in queue:
        return False
    return queue.index(int(review_id)) < len(queue) - 1


def _mp_reviews_keyboard(
    reviews: list,
    *,
    page: int = 0,
    bulk_count: int = 0,
) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    rows.append([*reviews_queue_toolbar()])
    if bulk_count > 0:
        rows.append(
            [
                InlineKeyboardButton(
                    text=f"⚡ Пакет 4–5★ ({bulk_count})",
                    callback_data="review:mp:bulk:preview",
                )
            ]
        )
    start = page * MP_LIST_PAGE_SIZE
    chunk = reviews[start : start + MP_LIST_PAGE_SIZE]
    for review in chunk:
        preview = (review.text or "—")[:40].replace("\n", " ")
        rating = f"⭐{review.rating}" if review.rating else "⭐?"
        if review.rating is not None and review.rating <= 3:
            rating = f"⚠️{review.rating}"
        rows.append(
            [
                InlineKeyboardButton(
                    text=f"{rating} {preview}",
                    callback_data=f"review:mp:pick:{review.id}",
                )
            ]
        )
    nav: list[InlineKeyboardButton] = []
    if start > 0:
        nav.append(
            InlineKeyboardButton(text="◀️ Назад", callback_data=f"review:mp:list:{page - 1}")
        )
    if start + MP_LIST_PAGE_SIZE < len(reviews):
        nav.append(
            InlineKeyboardButton(text="Ещё ▶️", callback_data=f"review:mp:list:{page + 1}")
        )
    if nav:
        rows.append(nav)
    rows.extend(nav_home_queue().inline_keyboard)
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
            [InlineKeyboardButton(text="❌ Отмена", callback_data="review:mp:cancel_publish")],
        ]
    )


async def _mp_variants_keyboard(
    session,
    db_user: DbUser,
    state: FSMContext,
    variants: list[str],
    selected: int,
    review_id: int,
) -> InlineKeyboardMarkup:
    base = await _build_variants_keyboard(session, db_user, state, len(variants), selected)
    rows = base.inline_keyboard[:-1]
    rows.append([InlineKeyboardButton(text="⏰ Отложить", callback_data=f"review:mp:snooze:{review_id}")])
    rows.extend(nav_home_queue().inline_keyboard)
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _pro_upsell_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🚀 Оформить PRO", callback_data="menu:subscription")],
            [InlineKeyboardButton(text="🎁 Trial PRO", callback_data="menu:trial_pro")],
        ]
    )


async def _mp_accounts(db_user: DbUser) -> list:
    session_factory = get_session_factory()
    async with session_factory() as session:
        accounts = await AccountRepository(session).list_by_user_id(db_user.id, active_only=True)
    return [a for a in accounts if a.marketplace in (Marketplace.WB, Marketplace.OZON)]


async def _execute_sync(callback: CallbackQuery, db_user: DbUser, account_ids: list[int] | None) -> None:
    session_factory = get_session_factory()
    total_new = 0
    errors: list[str] = []
    async with session_factory() as session:
        accounts = await AccountRepository(session).list_by_user_id(db_user.id, active_only=True)
        mp_accounts = [
            a
            for a in accounts
            if a.marketplace in (Marketplace.WB, Marketplace.OZON)
            and (account_ids is None or a.id in account_ids)
        ]
        settings = get_settings()
        for account in mp_accounts:
            try:
                created, _, new_reviews = await sync_account_reviews(session, account)
                total_new += created
                for review in new_reviews:
                    await try_auto_publish_review(
                        session, account=account, review=review, settings=settings
                    )
            except MarketplaceAPIError as exc:
                logger.warning("Sync failed account_id={} err={}", account.id, exc)
                msg = str(exc)
                if exc.status_code == 403 and account.marketplace == Marketplace.OZON:
                    msg += Ozon_FORBIDDEN_HINT
                errors.append(msg)
        await session.commit()

    lines = [SYNC_DONE.format(count=total_new)]
    if errors:
        lines.append("\nОшибки:\n" + "\n".join(f"• {e}" for e in errors[:5]))
    if callback.message:
        await callback.message.edit_text(
            "\n".join(lines),
            reply_markup=nav_home_queue(),
        )


@router.callback_query(F.data == "review:sync")
async def sync_reviews_menu(callback: CallbackQuery, db_user: DbUser) -> None:
    accounts = await _mp_accounts(db_user)
    if not accounts:
        await callback.answer()
        if callback.message:
            await safe_edit_message(
                callback.message,
                "⚠️ <b>Нет кабинетов</b>\n\nПодключите WB или Ozon, чтобы синхронизировать отзывы.",
                reply_markup=no_cabinets_keyboard(),
            )
        return
    if len(accounts) == 1:
        await callback.answer("Синхронизация…")
        await _execute_sync(callback, db_user, [accounts[0].id])
        return
    await callback.answer()
    if callback.message:
        await callback.message.edit_text(SYNC_INTRO, reply_markup=sync_accounts_keyboard(accounts))


@router.callback_query(F.data == "review:sync:all")
async def sync_reviews_all(callback: CallbackQuery, db_user: DbUser) -> None:
    await callback.answer("Синхронизация…")
    await _execute_sync(callback, db_user, None)


@router.callback_query(F.data.regexp(r"^review:sync:\d+$"))
async def sync_reviews_one(callback: CallbackQuery, db_user: DbUser) -> None:
    account_id = int(callback.data.split(":")[-1])
    await callback.answer("Синхронизация…")
    await _execute_sync(callback, db_user, [account_id])


@router.callback_query(F.data == "review:mp:list")
@router.callback_query(F.data.regexp(r"^review:mp:list:\d+$"))
async def list_mp_reviews(callback: CallbackQuery, state: FSMContext, db_user: DbUser) -> None:
    page = 0
    if callback.data.startswith("review:mp:list:"):
        page = max(0, int(callback.data.split(":")[-1]))
    session_factory = get_session_factory()
    async with session_factory() as session:
        accounts = await AccountRepository(session).list_by_user_id(db_user.id, active_only=True)
        mp_accounts = [a for a in accounts if a.marketplace in (Marketplace.WB, Marketplace.OZON)]
        if not mp_accounts:
            await callback.answer()
            if callback.message:
                await safe_edit_message(
                    callback.message,
                    MP_NO_CABINETS,
                    reply_markup=no_cabinets_keyboard(),
                )
            return
        reviews = await ReviewRepository(session).list_new_for_user(db_user.id, limit=30)
        bulk = await list_bulk_eligible(session, db_user.id)
    await state.update_data(mp_queue=[r.id for r in reviews])
    await callback.answer()
    if not reviews:
        text = MP_LIST_EMPTY
        kb = no_new_reviews_keyboard()
    else:
        shown_from = page * MP_LIST_PAGE_SIZE + 1
        shown_to = min(len(reviews), (page + 1) * MP_LIST_PAGE_SIZE)
        text = (
            f"{MP_LIST_HEADER}\n\n"
            f"В очереди: <b>{len(reviews)}</b> · показаны {shown_from}–{shown_to}"
        )
        kb = _mp_reviews_keyboard(reviews, page=page, bulk_count=len(bulk))
    if callback.message:
        await safe_edit_message(callback.message, text, reply_markup=kb)


@router.callback_query(F.data == "review:mp:bulk:preview")
async def mp_bulk_preview(callback: CallbackQuery, db_user: DbUser) -> None:
    session_factory = get_session_factory()
    async with session_factory() as session:
        eligible = await list_bulk_eligible(session, db_user.id)
        pro = await is_pro_user(session, db_user.id)
        can_pub, _ = await can_api_publish(session, db_user.id)
    if not eligible:
        await callback.answer("Нет подходящих отзывов", show_alert=True)
        return
    await callback.answer()
    text = (
        "⚡ <b>Пакетный ответ</b>\n\n"
        f"Подходит отзывов 4–5★ с коротким текстом: <b>{len(eligible)}</b>.\n"
        "Шаблон «Спасибо» — либо «обработан» для копирования, либо publish в API (PRO)."
    )
    rows: list[list[InlineKeyboardButton]] = [
        [InlineKeyboardButton(text="✅ Обработать (копия)", callback_data="review:mp:bulk:run")],
    ]
    if pro and can_pub:
        rows.insert(
            0,
            [
                InlineKeyboardButton(
                    text="🚀 PRO: publish в API",
                    callback_data="review:mp:bulk:run_api",
                )
            ],
        )
    rows.append([InlineKeyboardButton(text=REVIEWS_HUB_BUTTON, callback_data="review:mp:list")])
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    if callback.message:
        await safe_edit_message(callback.message, text, reply_markup=kb)


@router.callback_query(F.data == "review:mp:bulk:run_api")
async def mp_bulk_run_api(callback: CallbackQuery, db_user: DbUser) -> None:
    template = QUICK_REPLY_TEMPLATES["thanks"]
    session_factory = get_session_factory()
    async with session_factory() as session:
        published, _, failed = await apply_bulk_template_with_publish(
            session, user_id=db_user.id, template_text=template
        )
        await session.commit()
    await callback.answer("Готово")
    if callback.message:
        await callback.message.edit_text(
            f"🚀 Publish: <b>{published}</b> · ошибок: <b>{failed}</b>.",
            reply_markup=nav_home_queue(),
        )


@router.callback_query(F.data == "review:mp:bulk:run")
async def mp_bulk_run(callback: CallbackQuery, db_user: DbUser) -> None:
    template = QUICK_REPLY_TEMPLATES["thanks"]
    session_factory = get_session_factory()
    async with session_factory() as session:
        count = await apply_bulk_template(session, user_id=db_user.id, template_text=template)
        await session.commit()
    await callback.answer("Готово")
    if callback.message:
        await callback.message.edit_text(
            f"✅ Обработано отзывов: <b>{count}</b>.\n"
            "Откройте кабинет и вставьте тот же текст или ответьте из очереди по одному.",
            reply_markup=nav_home_queue(),
        )


async def _open_mp_review(
    review_id: int,
    callback: CallbackQuery,
    state: FSMContext,
    db_user: DbUser,
) -> None:
    data = await state.get_data()
    queue: list[int] = [int(x) for x in (data.get("mp_queue") or [])]
    if not queue:
        session_factory = get_session_factory()
        async with session_factory() as session:
            reviews = await ReviewRepository(session).list_new_for_user(db_user.id, limit=30)
        queue = [r.id for r in reviews]
        await state.update_data(mp_queue=queue)
    queue_pos = ""
    if review_id in queue:
        queue_pos = f"\n<i>Отзыв {queue.index(review_id) + 1} из {len(queue)}</i>"
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
        can_publish, _ = await can_api_publish(session, db_user.id)

    await state.update_data(
        review_id=review_id,
        review_text=review.text or "",
        rating=review.rating or 5,
        mp_flow=True,
    )
    await state.set_state(ManualReviewStates.waiting_tone)
    await callback.answer()
    if callback.message:
        card = format_review_card(review, account, can_publish_via_api=can_publish) + queue_pos
        await safe_edit_message(callback.message, card, reply_markup=tone_keyboard(profiles))


@router.callback_query(F.data.startswith("review:mp:pick:"))
async def mp_pick_review(callback: CallbackQuery, state: FSMContext, db_user: DbUser) -> None:
    review_id = int(callback.data.split(":")[-1])
    await _open_mp_review(review_id, callback, state, db_user)


@router.callback_query(
    ManualReviewStates.waiting_tone,
    F.data.startswith("review:tone:"),
    MpFlowFilter(),
)
async def mp_tone_generate(callback: CallbackQuery, state: FSMContext, db_user: DbUser) -> None:
    await _mp_generate_variants(callback, state, db_user, tone_key=callback.data.removeprefix("review:tone:"))


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
        allowed, _ = await can_api_publish(session, db_user.id)

    if callback.message:
        async with session_factory() as session:
            kb = await _mp_variants_keyboard(session, db_user, state, variants, index, review_id)
        await safe_edit_message(
            callback.message,
            _format_variants_message(variants, index, remaining),
            reply_markup=kb,
        )


@router.callback_query(
    MarketplaceReviewStates.viewing_variants,
    F.data == "review:more",
    MpFlowFilter(),
)
async def mp_more_variants(callback: CallbackQuery, state: FSMContext, db_user: DbUser) -> None:
    data = await state.get_data()
    tone_key = str(data.get("tone_key", "default"))
    await callback.answer("Генерирую…")
    if callback.message:
        await callback.message.edit_text("⏳ Генерирую ещё варианты…")
    await _mp_generate_variants(callback, state, db_user, tone_key=tone_key)


@router.callback_query(
    MarketplaceReviewStates.viewing_variants,
    F.data == "review:change_tone",
    MpFlowFilter(),
)
async def mp_change_tone(callback: CallbackQuery, state: FSMContext, db_user: DbUser) -> None:
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


async def _mp_generate_variants(
    callback: CallbackQuery,
    state: FSMContext,
    db_user: DbUser,
    *,
    tone_key: str,
) -> None:
    data = await state.get_data()
    review_text = data.get("review_text")
    rating = data.get("rating")
    review_id = data.get("review_id")
    if not review_text or rating is None:
        await state.clear()
        await callback.answer("Сессия сброшена", show_alert=True)
        return

    session_factory = get_session_factory()
    async with session_factory() as session:
        tone = await _tone_input(session, db_user.id, tone_key)

    if callback.message:
        await callback.message.edit_text("⏳ Генерирую варианты ответа…")

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
        allowed, _ = await can_api_publish(session, db_user.id)

    if callback.message:
        async with session_factory() as session:
            kb = await _mp_variants_keyboard(session, db_user, state, variants, 0, int(review_id))
        await safe_edit_message(
            callback.message,
            _format_variants_message(variants, 0, remaining),
            reply_markup=kb,
        )


@router.callback_query(MarketplaceReviewStates.viewing_variants, F.data == "review:mp:copy", MpFlowFilter())
async def mp_copy_answer(callback: CallbackQuery, state: FSMContext, db_user: DbUser) -> None:
    data = await state.get_data()
    variants: list[str] = data.get("variants") or []
    selected = int(data.get("selected_index", 0))
    review_id = data.get("review_id")
    if not variants:
        await callback.answer("Нет текста", show_alert=True)
        return
    text = variants[selected]
    clean, err = validate_reply_for_user(text)
    if err:
        await callback.answer(err, show_alert=True)
        return
    text = clean or text
    rid = int(review_id) if review_id is not None else None
    has_next = await _queue_has_next(state, rid)
    upsell: str | None = None
    if rid is not None:
        session_factory = get_session_factory()
        async with session_factory() as session:
            await _persist_selected_reply(session, rid, text, selected_index=selected)
            await ReviewRepository(session).update_status(rid, ReviewStatus.PROCESSED)
            upsell = await first_reply_upsell_suffix(session, db_user.id)
            await session.commit()
    await callback.answer("Скопируйте текст из сообщения")
    if callback.message:
        body = COPY_HINT.format(text=text)
        if upsell:
            body += upsell
        else:
            session_factory = get_session_factory()
            async with session_factory() as session:
                allowed, reason = await can_api_publish(session, db_user.id)
            if not allowed and reason == "need_pro":
                body += "\n\n💡 На PRO — публикация в WB/Ozon в один клик."
        await safe_edit_message(
            callback.message,
            body,
            reply_markup=after_review_action_keyboard(has_next=has_next, upsell=bool(upsell)),
        )
    await state.clear()


@router.callback_query(F.data.startswith("review:mp:publish:"))
async def mp_publish_ask_confirm(callback: CallbackQuery, state: FSMContext, db_user: DbUser) -> None:
    session_factory = get_session_factory()
    async with session_factory() as session:
        allowed, _ = await can_api_publish(session, db_user.id)
        if not allowed:
            await callback.answer(PRO_PUBLISH_REQUIRED, show_alert=True)
            return

    review_id = int(callback.data.split(":")[-1])
    data = await state.get_data()
    variants: list[str] = data.get("variants") or []
    selected = int(data.get("selected_index", 0))
    rating = int(data.get("rating") or 5)
    if not variants:
        await callback.answer("Сначала сгенерируйте варианты", show_alert=True)
        return
    text = variants[selected]
    await state.update_data(publish_text=text, publish_review_id=review_id)
    await state.set_state(MarketplaceReviewStates.awaiting_publish_confirm)
    await callback.answer()
    if callback.message:
        body = (
            NEGATIVE_PUBLISH_WARN.format(text=text)
            if rating <= 3
            else f"<b>Подтвердите публикацию</b>\n\n<code>{text}</code>"
        )
        await callback.message.edit_text(body, reply_markup=_publish_confirm_keyboard(review_id))


@router.callback_query(MarketplaceReviewStates.awaiting_publish_confirm, F.data.startswith("review:mp:confirm:"))
async def mp_publish_confirm(callback: CallbackQuery, state: FSMContext, db_user: DbUser) -> None:
    data = await state.get_data()
    text = data.get("publish_text")
    review_id = data.get("publish_review_id")
    if not text or review_id is None:
        await callback.answer("Данные устарели", show_alert=True)
        await state.clear()
        return

    session_factory = get_session_factory()
    async with session_factory() as session:
        allowed, _ = await can_api_publish(session, db_user.id)
        if not allowed:
            await callback.answer(
                "Закончилась бесплатная квота на публикацию в API. Оформите PRO или Trial.",
                show_alert=True,
            )
            return

    clean, err = validate_reply_for_user(str(text))
    if err:
        await callback.answer(err, show_alert=True)
        return

    await callback.answer("Публикую…")
    upsell: str | None = None
    try:
        async with session_factory() as session:
            review = await ReviewRepository(session).get_by_id(int(review_id))
            if review is None:
                raise MarketplaceAPIError("Отзыв не найден")
            account = await AccountRepository(session).get_by_id(review.account_id)
            if account is None or account.user_id != db_user.id:
                raise MarketplaceAPIError("Нет доступа к кабинету")
            selected = int(data.get("selected_index", 0))
            await _persist_selected_reply(session, int(review_id), clean or str(text), selected_index=selected)
            await publish_reply_to_marketplace(session, review, clean or str(text))
            upsell = await first_reply_upsell_suffix(session, db_user.id)
            await session.commit()
    except MarketplaceAPIError as exc:
        logger.warning("User publish failed review_id={} err={}", review_id, exc)
        if callback.message:
            await callback.message.edit_text(
                f"Не удалось опубликовать:\n\n{exc}",
                reply_markup=nav_home_queue(),
            )
        await state.clear()
        return

    has_next = await _queue_has_next(state, int(review_id))
    await state.clear()
    if callback.message:
        body = PUBLISH_SUCCESS + (upsell or "")
        await callback.message.edit_text(
            body,
            reply_markup=after_review_action_keyboard(has_next=has_next, upsell=bool(upsell)),
        )


@router.callback_query(F.data == "review:mp:cancel_publish")
async def mp_publish_cancel(callback: CallbackQuery, state: FSMContext, db_user: DbUser) -> None:
    await state.set_state(MarketplaceReviewStates.viewing_variants)
    await callback.answer("Отменено")
    data = await state.get_data()
    variants: list[str] = data.get("variants") or []
    review_id = int(data.get("review_id", 0))
    selected = int(data.get("selected_index", 0))
    if callback.message and variants:
        session_factory = get_session_factory()
        async with session_factory() as session:
            allowed, _ = await can_api_publish(session, db_user.id)
        async with session_factory() as session:
            kb = await _mp_variants_keyboard(session, db_user, state, variants, selected, review_id)
        await safe_edit_message(
            callback.message,
            _format_variants_message(variants, selected, None),
            reply_markup=kb,
        )


@router.callback_query(MarketplaceReviewStates.viewing_variants, F.data == "review:mp:edit", MpFlowFilter())
async def mp_edit_start(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(MarketplaceReviewStates.waiting_edit_text)
    await callback.answer()
    if callback.message:
        await safe_edit_message(
            callback.message,
            "✏️ Пришлите отредактированный текст ответа одним сообщением.",
        )


@router.message(MarketplaceReviewStates.waiting_edit_text, F.text)
async def mp_edit_apply(message: Message, state: FSMContext, db_user: DbUser) -> None:
    text = (message.text or "").strip()
    if len(text) < 3:
        await message.answer("Слишком коротко.")
        return
    clean, err = validate_reply_for_user(text)
    if err:
        await message.answer(err)
        return
    text = clean or text
    data = await state.get_data()
    variants: list[str] = data.get("variants") or []
    selected = int(data.get("selected_index", 0))
    if not variants:
        await state.clear()
        return
    variants[selected] = text
    await state.update_data(variants=variants)
    await state.set_state(MarketplaceReviewStates.viewing_variants)
    review_id = int(data.get("review_id", 0))
    session_factory = get_session_factory()
    async with session_factory() as session:
        await _persist_selected_reply(session, review_id, text, selected_index=selected)
        await session.commit()
    async with session_factory() as session:
        remaining = await remaining_generations_today(session, db_user.id)
        allowed, _ = await can_api_publish(session, db_user.id)
    async with session_factory() as session:
        kb = await _mp_variants_keyboard(session, db_user, state, variants, selected, review_id)
    await message.answer(
        _format_variants_message(variants, selected, remaining),
        reply_markup=kb,
    )


@router.callback_query(MarketplaceReviewStates.viewing_variants, F.data.startswith("review:quick:"), MpFlowFilter())
async def mp_quick_reply(callback: CallbackQuery, state: FSMContext, db_user: DbUser) -> None:
    key = callback.data.split(":")[-1]
    template = QUICK_REPLY_TEMPLATES.get(key)
    if not template:
        await callback.answer("Шаблон не найден")
        return
    data = await state.get_data()
    variants: list[str] = data.get("variants") or ["", "", ""]
    while len(variants) < 3:
        variants.append("")
    selected = int(data.get("selected_index", 0))
    variants[selected] = template
    review_id = int(data.get("review_id", 0))
    await state.update_data(variants=variants)
    await callback.answer("Шаблон подставлен")
    session_factory = get_session_factory()
    async with session_factory() as session:
        remaining = await remaining_generations_today(session, db_user.id)
        kb = await _mp_variants_keyboard(session, db_user, state, variants, selected, review_id)
    if callback.message:
        await safe_edit_message(
            callback.message,
            _format_variants_message(variants, selected, remaining),
            reply_markup=kb,
        )


@router.callback_query(F.data == "review:mp:next")
async def mp_next_review(callback: CallbackQuery, state: FSMContext, db_user: DbUser) -> None:
    data = await state.get_data()
    queue: list[int] = [int(x) for x in (data.get("mp_queue") or [])]
    current = data.get("review_id")
    session_factory = get_session_factory()
    if not queue:
        async with session_factory() as session:
            reviews = await ReviewRepository(session).list_new_for_user(db_user.id, limit=30)
        queue = [r.id for r in reviews]
    next_id: int | None = None
    if current is not None and int(current) in queue:
        idx = queue.index(int(current))
        if idx + 1 < len(queue):
            next_id = queue[idx + 1]
    if next_id is None and queue:
        next_id = queue[0]
    if next_id is None:
        await callback.answer("Нет отзывов в списке", show_alert=True)
        return
    await callback.answer()
    await _open_mp_review(next_id, callback, state, db_user)


@router.callback_query(F.data.startswith("review:mp:snooze:"))
async def mp_snooze(callback: CallbackQuery, db_user: DbUser) -> None:
    review_id = int(callback.data.split(":")[-1])
    until = datetime.now(UTC) + timedelta(days=1)
    session_factory = get_session_factory()
    async with session_factory() as session:
        review = await ReviewRepository(session).get_by_id_for_user(review_id, db_user.id)
        if review is None:
            await callback.answer("Не найден", show_alert=True)
            return
        await ReviewRepository(session).snooze(review_id, until)
        await session.commit()
    await callback.answer("Отложено на 24 ч")
    if callback.message:
        await callback.message.edit_text(
            f"⏰ Отзыв #{review_id} отложен до {format_ui_time(until)} (Минск).",
            reply_markup=nav_home_queue(),
        )
