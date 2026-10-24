from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from loguru import logger

from app.bot.keyboards.menu import main_menu_keyboard
from app.bot.utils.callbacks import safe_edit_message
from app.bot.keyboards.reviews import (
    history_filter_keyboard,
    manual_entry_keyboard,
    rating_keyboard,
    reviews_menu_keyboard,
    tone_keyboard,
    variants_keyboard,
)
from app.services.pro_access import can_api_publish
from app.bot.states.marketplace_review import MarketplaceReviewStates
from app.bot.states.review import ManualReviewStates
from app.core.config import get_settings
from app.db.models import ReviewStatus, User as DbUser
from app.db.repositories.account import AccountRepository
from app.services.marketplace.product_context import product_context_for_llm
from app.db.repositories.reply import ReplyRepository
from app.services.history_export import build_history_csv
from app.db.repositories.review import ReviewRepository
from app.db.repositories.tone_profile import ToneProfileRepository
from app.db.repositories.user import UserRepository
from app.db.session import get_session_factory
from app.services.generation_limit import can_generate, remaining_generations_today
from app.services.llm import LLMError, ToneProfileInput, generate_replies
from app.services.llm_queue import run_llm_job
from app.services.reply_templates import list_templates, template_by_id
from app.services.tone_resolver import resolve_tone_input
from app.services.manual_review import get_or_create_manual_account, new_manual_external_id

router = Router(name="reviews")

QUICK_REPLY_TEMPLATES = {
    "thanks": "Спасибо большое за отзыв! Нам очень приятно, что вы остались довольны покупкой. Хороших вам дней!",
    "glad": "Рады, что товар оправдал ожидания! Если появятся вопросы — мы на связи.",
}


async def _tone_input(session, user_id: int, tone_key: str):
    return await resolve_tone_input(session, user_id, tone_key)


def _format_variants_message(variants: list[str], selected_index: int, remaining: int | None) -> str:
    from app.bot.ui import muted, quote

    lines = ["<b>Варианты ответа</b>", muted("Нажмите цифру или «Править»"), ""]
    for index, text in enumerate(variants, start=1):
        if index - 1 == selected_index:
            lines.append(f"● <b>Вариант {index}</b>")
            lines.append(quote(text))
        else:
            short = text[:240] + ("…" if len(text) > 240 else "")
            lines.append(muted(f"{index}. {short}"))
    if remaining is not None:
        lines.append(muted(f"Генераций сегодня: {remaining} / 5"))
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


async def _llm_product_context(review_id: int) -> str | None:
    session_factory = get_session_factory()
    async with session_factory() as session:
        review = await ReviewRepository(session).get_by_id(review_id)
        if review is None:
            return None
        account = await AccountRepository(session).get_by_id(review.account_id)
        if account is None:
            return None
        return product_context_for_llm(review.raw_json, account.marketplace)


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
    product_context = await _llm_product_context(review_id)
    async with session_factory() as session:
        user = await UserRepository(session).get_by_id(user_id)
        soft_rec = bool(user and user.soft_product_recommend)

    async def _call_llm() -> list[str]:
        return await generate_replies(
            review_text,
            rating,
            tone,
            count=3,
            product_context=product_context,
            soft_product_recommend=soft_rec,
            settings=settings,
        )

    variants = await run_llm_job(_call_llm)

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


async def _build_variants_keyboard(
    session,
    db_user: DbUser,
    state: FSMContext,
    variant_count: int,
    selected_index: int,
) -> InlineKeyboardMarkup:
    data = await state.get_data()
    rating = int(data.get("rating") or 5)
    review_id_raw = data.get("review_id")
    mp_flow = bool(data.get("mp_flow"))
    queue: list[int] = [int(x) for x in (data.get("mp_queue") or [])]
    review_id = int(review_id_raw) if review_id_raw is not None else None
    has_next = bool(mp_flow and review_id is not None and review_id in queue and queue.index(review_id) < len(queue) - 1)
    can_publish = False
    if mp_flow:
        can_publish, _ = await can_api_publish(session, db_user.id)
    user = await UserRepository(session).get_by_id(db_user.id)
    templates = list_templates(user) if user else []
    return variants_keyboard(
        variant_count,
        selected_index,
        can_publish=can_publish,
        review_id=review_id if mp_flow else None,
        show_quick_templates=rating >= 4,
        has_next_in_queue=has_next,
        mp_mode=mp_flow,
        user_templates=templates,
    )


def _history_keyboard(reviews: list, reply_previews: dict[int, str]) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for item in reviews[:12]:
        review_bit = (item.text or "—")[:18].replace("\n", " ")
        answer_bit = reply_previews.get(item.id, "")
        if answer_bit:
            answer_bit = answer_bit[:22].replace("\n", " ")
            label = f"⭐{item.rating or '?'} {review_bit} → {answer_bit}"
        else:
            label = f"⭐{item.rating or '?'} {review_bit}"
        if len(label) > 60:
            label = label[:57] + "…"
        rows.append(
            [
                InlineKeyboardButton(
                    text=label,
                    callback_data=f"review:history:item:{item.id}",
                )
            ]
        )
    rows.append([InlineKeyboardButton(text="💬 Отзывы", callback_data="menu:reviews")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _history_statuses(key: str) -> tuple:
    if key == "published":
        return (ReviewStatus.PUBLISHED,)
    if key == "copied":
        return (ReviewStatus.PROCESSED,)
    return (ReviewStatus.PROCESSED, ReviewStatus.PUBLISHED)


async def _render_history(
    db_user: DbUser,
    *,
    filter_key: str = "all",
    account_id: int | None = None,
) -> tuple[str, InlineKeyboardMarkup]:
    session_factory = get_session_factory()
    async with session_factory() as session:
        accounts = await AccountRepository(session).list_by_user_id(db_user.id)
        reviews = await ReviewRepository(session).list_by_user(
            db_user.id,
            statuses=_history_statuses(filter_key),
            account_id=account_id,
            limit=20,
        )
        reply_previews = await ReplyRepository(session).latest_text_by_review_ids(
            [r.id for r in reviews]
        )
    if not reviews:
        text = "📚 <b>История пуста</b>\n\n" + "<i>👇 Ответьте на отзыв — здесь появятся копии и publish.</i>"
        kb = reviews_menu_keyboard()
    else:
        label = {"all": "все", "published": "publish", "copied": "копия"}.get(filter_key, "все")
        text = f"📚 <b>История</b> ({label})\n\nНажмите на отзыв:"
        kb = _history_keyboard(reviews, reply_previews)
        filter_kb = history_filter_keyboard(
            current=filter_key,
            account_id=account_id,
            accounts=[a for a in accounts if a.marketplace.value in ("wb", "ozon")],
        )
        kb = InlineKeyboardMarkup(
            inline_keyboard=filter_kb.inline_keyboard + kb.inline_keyboard,
        )
    return text, kb


@router.callback_query(F.data == "review:history:export")
async def review_history_export(callback: CallbackQuery, db_user: DbUser) -> None:
    session_factory = get_session_factory()
    async with session_factory() as session:
        payload = await build_history_csv(session, db_user.id)
    await callback.answer()
    if callback.message:
        await callback.message.answer_document(
            BufferedInputFile(payload, filename="golos-brenda-history.csv"),
            caption="📥 История отзывов (до 2000 строк, UTF-8 для Excel)",
        )


@router.callback_query(F.data == "review:history")
async def review_history(callback: CallbackQuery, db_user: DbUser) -> None:
    await callback.answer()
    text, kb = await _render_history(db_user)
    if callback.message:
        await safe_edit_message(callback.message, text, reply_markup=kb)


@router.callback_query(F.data.startswith("review:history:filter:"))
async def review_history_filter(callback: CallbackQuery, db_user: DbUser) -> None:
    key = callback.data.split(":")[-1]
    await callback.answer()
    text, kb = await _render_history(db_user, filter_key=key)
    if callback.message:
        await safe_edit_message(callback.message, text, reply_markup=kb)


@router.callback_query(F.data.startswith("review:history:acc:"))
async def review_history_account(callback: CallbackQuery, db_user: DbUser) -> None:
    acc_raw = int(callback.data.split(":")[-1])
    account_id = None if acc_raw == 0 else acc_raw
    await callback.answer()
    text, kb = await _render_history(db_user, account_id=account_id)
    if callback.message:
        await safe_edit_message(callback.message, text, reply_markup=kb)


@router.callback_query(F.data.startswith("review:history:item:"))
async def review_history_item(callback: CallbackQuery, db_user: DbUser) -> None:
    review_id = int(callback.data.split(":")[-1])
    session_factory = get_session_factory()
    async with session_factory() as session:
        review = await ReviewRepository(session).get_by_id_for_user(review_id, db_user.id)
        if review is None:
            await callback.answer("Не найден", show_alert=True)
            return
        replies = await ReplyRepository(session).list_by_review_id(review_id)
    if review.status == ReviewStatus.PUBLISHED:
        status = "🟢 опубликован в API"
    else:
        status = "📋 скопирован (Lite)"
    lines = [
        f"<b>Отзыв #{review.id}</b> · {status}",
        f"⭐ {review.rating or '?'}",
        "",
        review.text or "—",
        "",
        "<b>Ответы:</b>",
    ]
    if replies:
        for reply in replies[-3:]:
            lines.append(f"• {reply.text[:300]}")
    else:
        lines.append("—")
    await callback.answer()
    if callback.message:
        await callback.message.edit_text(
            "\n".join(lines),
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="📚 История", callback_data="review:history")],
                ]
            ),
        )


@router.callback_query(ManualReviewStates.viewing_variants, F.data == "review:edit")
async def manual_edit_start(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(ManualReviewStates.waiting_edit_text)
    await callback.answer()
    if callback.message:
        from app.bot.utils.callbacks import safe_edit_message

        await safe_edit_message(
            callback.message,
            "✏️ Пришлите исправленный текст ответа.",
        )


@router.message(ManualReviewStates.waiting_edit_text, F.text)
async def manual_edit_apply(message: Message, state: FSMContext, db_user: DbUser) -> None:
    text = (message.text or "").strip()
    data = await state.get_data()
    variants: list[str] = data.get("variants") or []
    selected = int(data.get("selected_index", 0))
    if not variants:
        await state.clear()
        return
    variants[selected] = text
    await state.update_data(variants=variants)
    await state.set_state(ManualReviewStates.viewing_variants)
    session_factory = get_session_factory()
    async with session_factory() as session:
        remaining = await remaining_generations_today(session, db_user.id)
    async with session_factory() as session:
        kb = await _build_variants_keyboard(session, db_user, state, len(variants), selected)
    await message.answer(
        _format_variants_message(variants, selected, remaining),
        reply_markup=kb,
    )


@router.callback_query(F.data == "menu:reviews")
async def menu_reviews(callback: CallbackQuery, state: FSMContext, db_user: DbUser) -> None:
    """Сразу в очередь — без промежуточного экрана «Отзывы»."""
    from app.bot.handlers.marketplace_reviews import list_mp_reviews

    await state.clear()
    await list_mp_reviews(callback, state, db_user)


@router.callback_query(F.data == "menu:main")
async def menu_main(callback: CallbackQuery, state: FSMContext, db_user: DbUser) -> None:
    from app.bot.handlers.dashboard import _edit_dashboard

    await state.clear()
    await callback.answer()
    if callback.message:
        await _edit_dashboard(callback.message, db_user)


@router.callback_query(F.data == "review:manual:start")
async def manual_start(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(ManualReviewStates.waiting_text)
    await callback.answer()
    if callback.message:
        await safe_edit_message(
            callback.message,
            "✍️ <b>Ручной ответ</b>\n\n"
            "Отзыва нет в sync — вставьте текст сами.\n"
            "Пришлите <b>текст отзыва</b> одним сообщением.",
            reply_markup=manual_entry_keyboard(),
        )


@router.callback_query(F.data == "review:cancel")
async def review_cancel(callback: CallbackQuery, state: FSMContext, db_user: DbUser) -> None:
    await state.clear()
    await callback.answer("Отменено")
    from app.bot.handlers.marketplace_reviews import list_mp_reviews

    await list_mp_reviews(callback, state, db_user)


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
        kb = await _build_variants_keyboard(session, db_user, state, len(variants), 0)

    if callback.message:
        await safe_edit_message(
            callback.message,
            _format_variants_message(variants, 0, remaining),
            reply_markup=kb,
        )


@router.callback_query(ManualReviewStates.viewing_variants, F.data.startswith("review:quick:"))
async def manual_quick_reply(callback: CallbackQuery, state: FSMContext, db_user: DbUser) -> None:
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
    await state.update_data(variants=variants)
    await callback.answer("Шаблон подставлен")
    session_factory = get_session_factory()
    async with session_factory() as session:
        remaining = await remaining_generations_today(session, db_user.id)
        kb = await _build_variants_keyboard(session, db_user, state, len(variants), selected)
    if callback.message:
        await safe_edit_message(
            callback.message,
            _format_variants_message(variants, selected, remaining),
            reply_markup=kb,
        )


@router.callback_query(F.data.startswith("review:user_tpl:"))
async def apply_user_template(callback: CallbackQuery, state: FSMContext, db_user: DbUser) -> None:
    state_name = await state.get_state()
    allowed = {
        ManualReviewStates.viewing_variants.state,
        MarketplaceReviewStates.viewing_variants.state,
    }
    if state_name not in allowed:
        await callback.answer("Сначала сгенерируйте варианты")
        return
    template_id = callback.data.split(":")[-1]
    session_factory = get_session_factory()
    async with session_factory() as session:
        user = await UserRepository(session).get_by_id(db_user.id)
        tpl = template_by_id(user, template_id) if user else None
    if not tpl:
        await callback.answer("Шаблон не найден", show_alert=True)
        return
    data = await state.get_data()
    variants: list[str] = data.get("variants") or ["", "", ""]
    while len(variants) < 3:
        variants.append("")
    selected = int(data.get("selected_index", 0))
    variants[selected] = tpl["text"]
    await state.update_data(variants=variants)
    await callback.answer(f"📝 {tpl['label']}")
    async with session_factory() as session:
        remaining = await remaining_generations_today(session, db_user.id)
        kb = await _build_variants_keyboard(session, db_user, state, len(variants), selected)
    if callback.message:
        await safe_edit_message(
            callback.message,
            _format_variants_message(variants, selected, remaining),
            reply_markup=kb,
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
        kb = await _build_variants_keyboard(session, db_user, state, len(variants), index)

    if callback.message:
        await safe_edit_message(
            callback.message,
            _format_variants_message(variants, index, remaining),
            reply_markup=kb,
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
        from app.bot.utils.callbacks import safe_edit_message

        await safe_edit_message(
            callback.message,
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
        await callback.answer("Откройте «Ответы на отзывы»", show_alert=True)
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
        kb = await _build_variants_keyboard(session, db_user, state, len(variants), 0)

    if callback.message:
        await safe_edit_message(
            callback.message,
            _format_variants_message(variants, 0, remaining),
            reply_markup=kb,
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
