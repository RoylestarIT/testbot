from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from app.bot.copy import NOTIFICATIONS_INTRO, SETTINGS_INTRO as SETTINGS_TEXT
from app.services.notification_previews import (
    preview_buyer_questions,
    preview_daily_digest,
    preview_new_reviews,
    preview_stale_reviews,
)
from app.bot.utils.callbacks import safe_edit_message
from app.bot.wb_key_guide import (
    parse_wb_help_context,
    send_wb_key_album,
    wb_key_guide_keyboard,
    wb_key_guide_text,
)
from app.bot.handlers.onboarding import onboarding_finished_screen
from app.bot.utils.ui_message import bind_ui_message, edit_bound_ui_message
from app.services.onboarding_checklist import try_complete_onboarding
from app.bot.keyboards.menu import main_menu_keyboard
from app.bot.keyboards.autopublish import autopublish_detail_keyboard
from app.bot.keyboards.settings import (
    account_detail_keyboard,
    accounts_menu_keyboard,
    autopublish_accounts_keyboard,
    settings_menu_keyboard,
    tone_detail_keyboard,
    tone_menu_keyboard,
)
from app.db.models import MarketplaceAccount
from app.bot.states.settings import (
    AutoStopWordsStates,
    ConnectOzonStates,
    ConnectWbStates,
    ReplyTemplateStates,
    RotateOzonKeyStates,
    RotateWbKeyStates,
    ToneProfileStates,
)
from app.core.security import EncryptionError
from app.db.models import Marketplace, User as DbUser
from app.db.repositories.account import AccountRepository
from app.db.repositories.user import UserRepository
from app.db.repositories.tone_profile import ToneProfileRepository
from app.db.session import get_session_factory
from app.services.marketplace.account_connect import (
    test_and_create_ozon_account,
    test_and_create_wb_account,
    test_and_update_ozon_credentials,
    test_and_update_wb_api_key,
)
from app.services.marketplace.connect_sync import connect_success_keyboard, sync_new_account_reviews
from app.services.marketplace.sync_service import sync_account_reviews
from app.tasks.poller import format_ui_time
from app.services.reply_templates import add_template, list_templates, remove_template
from app.services.generation_limit import is_pro_user
from app.services.marketplace.base import MarketplaceAPIError
from app.services.marketplace.wildberries import normalize_wb_api_key, wb_token_is_test
from app.services.plans import (
    FREE_MAX_MARKETPLACE_ACCOUNTS,
    FREE_MAX_TONE_PROFILES,
    can_add_marketplace_account,
    max_marketplace_accounts,
    can_add_tone_profile,
    count_user_api_accounts,
    count_user_tone_profiles,
    has_lite_or_higher,
)

router = Router(name="settings")


def _notifications_screen_text(*, preview_block: str | None = None) -> str:
    if not preview_block:
        return NOTIFICATIONS_INTRO
    return f"{NOTIFICATIONS_INTRO}\n\n───────────────\n{preview_block}"


@router.callback_query(F.data == "menu:settings")
async def menu_settings(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.answer()
    if callback.message:
        await safe_edit_message(
            callback.message, SETTINGS_TEXT, reply_markup=settings_menu_keyboard()
        )


def _autopublish_detail_text(account: MarketplaceAccount) -> str:
    mp = "Wildberries" if account.marketplace == Marketplace.WB else "Ozon"
    name = account.shop_name or f"{mp} #{account.id}"
    min_r = account.auto_publish_min_rating or 4
    rule = "только <b>5★</b>" if min_r >= 5 else "<b>4–5★</b>"
    stars_only = "да" if account.auto_publish_stars_only else "нет"
    stops = (account.auto_publish_stop_words or "").strip() or "—"
    state = "включена" if account.auto_publish_enabled else "выключена"
    return (
        f"<b>Авто-публикация</b> · {name}\n\n"
        f"Статус: <b>{state}</b>\n"
        f"Звёзды: {rule} · 1–3★ всегда вручную\n"
        f"Только оценка без текста: <b>{stars_only}</b>\n"
        f"Стоп-слова: <i>{stops[:120]}</i>"
    )


@router.callback_query(F.data == "pro:autopublish")
async def pro_autopublish_menu(callback: CallbackQuery, db_user: DbUser) -> None:
    session_factory = get_session_factory()
    async with session_factory() as session:
        accounts = await AccountRepository(session).list_by_user_id(db_user.id, active_only=True)
    await callback.answer()
    if callback.message:
        await safe_edit_message(
            callback.message,
            "<b>Авто-публикация (PRO)</b>\n\n"
            "Выберите кабинет — на следующем экране правила (4–5★ или только 5★).",
            reply_markup=autopublish_accounts_keyboard(accounts),
        )


@router.callback_query(F.data.startswith("settings:autopublish:detail:"))
async def settings_autopublish_detail(callback: CallbackQuery, db_user: DbUser) -> None:
    account_id = int(callback.data.split(":")[-1])
    session_factory = get_session_factory()
    async with session_factory() as session:
        if not await is_pro_user(session, db_user.id):
            await callback.answer("Только для PRO", show_alert=True)
            return
        account = await AccountRepository(session).get_by_id(account_id)
        if account is None or account.user_id != db_user.id:
            await callback.answer("Нет доступа", show_alert=True)
            return
    await callback.answer()
    if callback.message and account is not None:
        await safe_edit_message(
            callback.message,
            _autopublish_detail_text(account),
            reply_markup=autopublish_detail_keyboard(account),
        )


@router.callback_query(F.data == "settings:accounts")
async def settings_accounts(callback: CallbackQuery, db_user: DbUser) -> None:
    session_factory = get_session_factory()
    async with session_factory() as session:
        accounts = await AccountRepository(session).list_by_user_id(db_user.id)
        api_count = await count_user_api_accounts(session, db_user.id)
        cab_limit = await max_marketplace_accounts(session, db_user.id)
    await callback.answer()
    limit_line = f"Кабинеты WB/Ozon: <b>{api_count}/{cab_limit}</b> на вашем тарифе."
    text = f"<b>Кабинеты маркетплейсов</b>\n\n{limit_line}"
    if callback.message:
        await safe_edit_message(
            callback.message,text, reply_markup=accounts_menu_keyboard(accounts))


@router.callback_query(F.data.startswith("help:wb_key"))
async def help_wb_key(callback: CallbackQuery) -> None:
    action, ctx = parse_wb_help_context(callback.data or "")
    await callback.answer()
    if callback.message is None:
        return
    if action == "album":
        await send_wb_key_album(callback.bot, callback.message.chat.id)
        await callback.message.answer(
            wb_key_guide_text(),
            reply_markup=wb_key_guide_keyboard(context=ctx),
        )
        return
    await safe_edit_message(
        callback.message,
        wb_key_guide_text(),
        reply_markup=wb_key_guide_keyboard(context=ctx),
    )


@router.callback_query(F.data == "settings:connect:wb")
async def connect_wb_start(callback: CallbackQuery, state: FSMContext, db_user: DbUser) -> None:
    session_factory = get_session_factory()
    async with session_factory() as session:
        allowed, msg = await can_add_marketplace_account(session, db_user.id)
    if not allowed:
        await callback.answer(msg or "Лимит кабинетов", show_alert=True)
        return
    await state.set_state(ConnectWbStates.waiting_api_key)
    await callback.answer()
    if callback.message:
        await safe_edit_message(
            callback.message,
            "<b>Wildberries</b>\n\n"
            "Нужен API-ключ с доступом «Вопросы и отзывы». "
            "Ниже — пошаговая инструкция с карточками.\n\n"
            "Когда ключ готов — пришлите его <b>одним сообщением</b>.\n"
            "Ключ храним в зашифрованном виде.",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="📖 Инструкция (7 шагов)", callback_data="help:wb_key:connect")],
                    [InlineKeyboardButton(text="🖼 Карточки", callback_data="help:wb_key:album:connect")],
                    [InlineKeyboardButton(text="◀️ Назад", callback_data="settings:accounts")],
                ]
            ),
        )


@router.message(ConnectWbStates.waiting_api_key, F.text)
async def connect_wb_api_key(message: Message, state: FSMContext) -> None:
    key = normalize_wb_api_key(message.text or "")
    if len(key) < 10:
        await message.answer("Ключ слишком короткий. Проверьте и отправьте снова.")
        return
    await state.update_data(wb_api_key=key)
    await state.set_state(ConnectWbStates.waiting_shop_name)
    await message.answer(
        "Укажите название магазина (для отображения в меню) или отправьте «-» без названия."
    )


@router.message(ConnectWbStates.waiting_shop_name, F.text)
async def connect_wb_finish(message: Message, state: FSMContext, db_user: DbUser) -> None:
    data = await state.get_data()
    api_key = data.get("wb_api_key")
    if not api_key:
        await state.clear()
        await message.answer("Сессия сброшена. Начните подключение заново.")
        return
    raw_name = (message.text or "").strip()
    shop_name = None if raw_name in {"", "-", "—"} else raw_name[:255]

    session_factory = get_session_factory()
    try:
        async with session_factory() as session:
            allowed, limit_msg = await can_add_marketplace_account(session, db_user.id)
            if not allowed:
                await message.answer(limit_msg or "Лимит кабинетов.", reply_markup=settings_menu_keyboard())
                await state.clear()
                return
            account, sample = await test_and_create_wb_account(
                session,
                user_id=db_user.id,
                api_key=str(api_key),
                shop_name=shop_name,
            )
            await session.commit()
    except EncryptionError:
        await message.answer(
            "Сейчас нельзя сохранить ключ — напишите в поддержку.",
            reply_markup=settings_menu_keyboard(),
        )
        await state.clear()
        return
    except MarketplaceAPIError as exc:
        await message.answer(
            f"Не удалось проверить ключ WB:\n\n{exc}",
            reply_markup=settings_menu_keyboard(),
        )
        await state.clear()
        return

    await state.clear()
    hint = "Тестовый запрос выполнен." if sample is None else "Получен 1 отзыв — ключ работает."
    if wb_token_is_test(str(api_key)):
        hint += (
            "\n\n🧪 Это <b>тестовый</b> токен WB (sandbox): данные демо, не отзывы вашего магазина. "
            "Для продакшена создайте персональный токен с категорией «Вопросы и отзывы»."
        )
    sync_line = ""
    try:
        async with session_factory() as session:
            acc = await AccountRepository(session).get_by_id(account.id)
            if acc is not None:
                new_n, auto_n, queue_n = await sync_new_account_reviews(session, acc)
                await session.commit()
                sync_line = (
                    f"\n🔄 Первая синхронизация: новых <b>{new_n}</b>"
                    f" (авто PRO: {auto_n}, в очереди: {queue_n})."
                )
    except MarketplaceAPIError as exc:
        sync_line = f"\n⚠️ Sync: {exc}"
    await message.answer(
        f"✅ Wildberries подключён (кабинет #{account.id}).\n{hint}{sync_line}",
        reply_markup=connect_success_keyboard(),
    )


@router.callback_query(F.data == "settings:connect:ozon")
async def connect_ozon_start(callback: CallbackQuery, state: FSMContext, db_user: DbUser) -> None:
    session_factory = get_session_factory()
    async with session_factory() as session:
        allowed, msg = await can_add_marketplace_account(session, db_user.id)
    if not allowed:
        await callback.answer(msg or "Лимит кабинетов", show_alert=True)
        return
    await state.set_state(ConnectOzonStates.waiting_client_id)
    await callback.answer()
    if callback.message:
        await safe_edit_message(
            callback.message,
            "<b>Ozon</b>\n\nПришлите <b>Client-Id</b> из кабинета продавца.",
        )


@router.message(ConnectOzonStates.waiting_client_id, F.text)
async def connect_ozon_client_id(message: Message, state: FSMContext) -> None:
    client_id = (message.text or "").strip()
    if not client_id.isdigit():
        await message.answer("Client-Id обычно числовой. Отправьте корректное значение.")
        return
    await state.update_data(ozon_client_id=client_id)
    await state.set_state(ConnectOzonStates.waiting_api_key)
    await message.answer("Теперь пришлите <b>Api-Key</b> Ozon Seller API.")


@router.message(ConnectOzonStates.waiting_api_key, F.text)
async def connect_ozon_api_key(message: Message, state: FSMContext) -> None:
    key = (message.text or "").strip()
    if len(key) < 8:
        await message.answer("Api-Key слишком короткий.")
        return
    await state.update_data(ozon_api_key=key)
    await state.set_state(ConnectOzonStates.waiting_shop_name)
    await message.answer("Название магазина (или «-»):")


@router.message(ConnectOzonStates.waiting_shop_name, F.text)
async def connect_ozon_finish(message: Message, state: FSMContext, db_user: DbUser) -> None:
    data = await state.get_data()
    client_id = data.get("ozon_client_id")
    api_key = data.get("ozon_api_key")
    if not client_id or not api_key:
        await state.clear()
        await message.answer("Сессия сброшена.")
        return
    raw_name = (message.text or "").strip()
    shop_name = None if raw_name in {"", "-", "—"} else raw_name[:255]

    session_factory = get_session_factory()
    try:
        async with session_factory() as session:
            allowed, limit_msg = await can_add_marketplace_account(session, db_user.id)
            if not allowed:
                await message.answer(limit_msg or "Лимит кабинетов.", reply_markup=settings_menu_keyboard())
                await state.clear()
                return
            account, sample = await test_and_create_ozon_account(
                session,
                user_id=db_user.id,
                client_id=str(client_id),
                api_key=str(api_key),
                shop_name=shop_name,
            )
            await session.commit()
    except EncryptionError:
        await message.answer("FERNET_KEY не настроен.", reply_markup=settings_menu_keyboard())
        await state.clear()
        return
    except MarketplaceAPIError as exc:
        await message.answer(f"Ozon: проверка не прошла:\n\n{exc}", reply_markup=settings_menu_keyboard())
        await state.clear()
        return

    await state.clear()
    hint = "Отзывов в выборке нет." if sample is None else "Получен отзыв — ключи работают."
    sync_line = ""
    try:
        async with session_factory() as session:
            acc = await AccountRepository(session).get_by_id(account.id)
            if acc is not None:
                new_n, auto_n, queue_n = await sync_new_account_reviews(session, acc)
                await session.commit()
                sync_line = (
                    f"\n🔄 Первая синхронизация: новых <b>{new_n}</b>"
                    f" (авто PRO: {auto_n}, в очереди: {queue_n})."
                )
    except MarketplaceAPIError as exc:
        sync_line = f"\n⚠️ Sync: {exc}"
    await message.answer(
        f"✅ Ozon подключён (кабинет #{account.id}).\n{hint}{sync_line}",
        reply_markup=connect_success_keyboard(),
    )


@router.callback_query(F.data.regexp(r"^settings:account:\d+$"))
async def settings_account_detail(callback: CallbackQuery, db_user: DbUser) -> None:
    account_id = int(callback.data.split(":")[-1])
    session_factory = get_session_factory()
    async with session_factory() as session:
        account = await AccountRepository(session).get_by_id(account_id)
        is_pro = await is_pro_user(session, db_user.id)
    if account is None or account.user_id != db_user.id:
        await callback.answer("Кабинет не найден", show_alert=True)
        return
    mp = "Wildberries" if account.marketplace == Marketplace.WB else "Ozon"
    name = account.shop_name or f"{mp} #{account.id}"
    sync_hint = ""
    if account.last_sync_at:
        sync_hint = f"\n🔄 Sync: {format_ui_time(account.last_sync_at)} (Минск)"
    if account.last_sync_error:
        sync_hint += f"\n⚠️ {account.last_sync_error[:200]}"
    key_status = "✅ ключ OK" if account.is_active and not account.last_sync_error else "⚠️ проверьте ключ"
    await callback.answer()
    if callback.message:
        await safe_edit_message(
            callback.message,
            f"<b>{name}</b>\nПлощадка: {mp}\n{key_status}"
            f"{sync_hint}",
            reply_markup=account_detail_keyboard(
                account.id,
                account.is_active,
                auto_publish_enabled=account.auto_publish_enabled,
                show_auto_publish=is_pro and account.marketplace in (Marketplace.WB, Marketplace.OZON),
            ),
        )


@router.callback_query(F.data.startswith("settings:account_autopublish:"))
async def settings_account_autopublish(callback: CallbackQuery, db_user: DbUser) -> None:
    account_id = int(callback.data.split(":")[-1])
    session_factory = get_session_factory()
    async with session_factory() as session:
        if not await is_pro_user(session, db_user.id):
            await callback.answer("Только для PRO", show_alert=True)
            return
        repo = AccountRepository(session)
        account = await repo.get_by_id(account_id)
        if account is None or account.user_id != db_user.id:
            await callback.answer("Нет доступа", show_alert=True)
            return
        account = await repo.set_auto_publish(account_id, not account.auto_publish_enabled)
        await session.commit()
    await callback.answer("Сохранено")
    if callback.message and account is not None:
        await safe_edit_message(
            callback.message,
            _autopublish_detail_text(account),
            reply_markup=autopublish_detail_keyboard(account),
        )


@router.callback_query(F.data.startswith("settings:autopublish_min:"))
async def settings_autopublish_min_rating(callback: CallbackQuery, db_user: DbUser) -> None:
    account_id = int(callback.data.split(":")[-1])
    session_factory = get_session_factory()
    async with session_factory() as session:
        if not await is_pro_user(session, db_user.id):
            await callback.answer("Только для PRO", show_alert=True)
            return
        repo = AccountRepository(session)
        account = await repo.get_by_id(account_id)
        if account is None or account.user_id != db_user.id:
            await callback.answer("Нет доступа", show_alert=True)
            return
        new_min = 5 if (account.auto_publish_min_rating or 4) < 5 else 4
        account = await repo.set_auto_publish_min_rating(account_id, new_min)
        await session.commit()
    await callback.answer("Правило обновлено")
    if callback.message and account is not None:
        await safe_edit_message(
            callback.message,
            _autopublish_detail_text(account),
            reply_markup=autopublish_detail_keyboard(account),
        )


@router.callback_query(F.data.startswith("settings:autopublish_empty:"))
async def settings_autopublish_stars_only(callback: CallbackQuery, db_user: DbUser) -> None:
    account_id = int(callback.data.split(":")[-1])
    session_factory = get_session_factory()
    async with session_factory() as session:
        if not await is_pro_user(session, db_user.id):
            await callback.answer("Только для PRO", show_alert=True)
            return
        repo = AccountRepository(session)
        account = await repo.get_by_id(account_id)
        if account is None or account.user_id != db_user.id:
            await callback.answer("Нет доступа", show_alert=True)
            return
        account = await repo.toggle_auto_publish_stars_only(account_id)
        await session.commit()
    await callback.answer("Сохранено")
    if callback.message and account is not None:
        await safe_edit_message(
            callback.message,
            _autopublish_detail_text(account),
            reply_markup=autopublish_detail_keyboard(account),
        )


@router.callback_query(F.data.startswith("settings:autopublish_stops:"))
async def settings_autopublish_stops_start(
    callback: CallbackQuery, state: FSMContext, db_user: DbUser
) -> None:
    account_id = int(callback.data.split(":")[-1])
    session_factory = get_session_factory()
    async with session_factory() as session:
        if not await is_pro_user(session, db_user.id):
            await callback.answer("Только для PRO", show_alert=True)
            return
        account = await AccountRepository(session).get_by_id(account_id)
        if account is None or account.user_id != db_user.id:
            await callback.answer("Нет доступа", show_alert=True)
            return
    await state.set_state(AutoStopWordsStates.waiting_words)
    await state.update_data(autopublish_stop_account_id=account_id)
    await callback.answer()
    current = (account.auto_publish_stop_words or "").strip() or "—"
    if callback.message:
        await safe_edit_message(
            callback.message,
            "<b>Стоп-слова для авто-публикации</b>\n\n"
            "Если в тексте отзыва есть одно из слов — авто не сработает, отзыв останется в очереди.\n\n"
            f"Сейчас: <i>{current[:200]}</i>\n\n"
            "Пришлите список через запятую или с новой строки.\n"
            "Чтобы очистить — отправьте «-».",
        )


@router.message(AutoStopWordsStates.waiting_words, F.text)
async def settings_autopublish_stops_save(
    message: Message, state: FSMContext, db_user: DbUser
) -> None:
    data = await state.get_data()
    account_id = int(data.get("autopublish_stop_account_id", 0))
    raw = (message.text or "").strip()
    words: str | None
    if raw in {"", "-", "—"}:
        words = None
    else:
        words = raw[:512]

    session_factory = get_session_factory()
    async with session_factory() as session:
        if not await is_pro_user(session, db_user.id):
            await state.clear()
            await message.answer("Только для PRO.", reply_markup=settings_menu_keyboard())
            return
        repo = AccountRepository(session)
        account = await repo.get_by_id(account_id)
        if account is None or account.user_id != db_user.id:
            await state.clear()
            await message.answer("Кабинет не найден.", reply_markup=settings_menu_keyboard())
            return
        account = await repo.set_auto_publish_stop_words(account_id, words)
        await session.commit()
    await state.clear()
    if account is None:
        await message.answer("Не удалось сохранить.", reply_markup=settings_menu_keyboard())
        return
    await message.answer(
        "✅ Стоп-слова сохранены.",
        reply_markup=autopublish_detail_keyboard(account),
    )
    await message.answer(_autopublish_detail_text(account))


@router.callback_query(F.data.startswith("settings:account_toggle:"))
async def settings_account_toggle(callback: CallbackQuery, db_user: DbUser) -> None:
    account_id = int(callback.data.split(":")[-1])
    session_factory = get_session_factory()
    async with session_factory() as session:
        repo = AccountRepository(session)
        account = await repo.get_by_id(account_id)
        if account is None or account.user_id != db_user.id:
            await callback.answer("Нет доступа", show_alert=True)
            return
        account = await repo.set_active(account_id, not account.is_active)
        await session.commit()
    await callback.answer("Обновлено")
    if callback.message and account is not None:
        mp = "Wildberries" if account.marketplace == Marketplace.WB else "Ozon"
        name = account.shop_name or f"{mp} #{account.id}"
        async with session_factory() as session:
            is_pro = await is_pro_user(session, db_user.id)
        await safe_edit_message(
            callback.message,
            f"<b>{name}</b>\nПлощадка: {mp}\nСтатус: {'активен' if account.is_active else 'отключён'}",
            reply_markup=account_detail_keyboard(
                account.id,
                account.is_active,
                auto_publish_enabled=account.auto_publish_enabled,
                show_auto_publish=is_pro and account.marketplace in (Marketplace.WB, Marketplace.OZON),
            ),
        )


@router.callback_query(F.data.regexp(r"^settings:account_rotate:\d+$"))
async def settings_account_rotate_start(callback: CallbackQuery, state: FSMContext, db_user: DbUser) -> None:
    account_id = int(callback.data.split(":")[-1])
    session_factory = get_session_factory()
    async with session_factory() as session:
        account = await AccountRepository(session).get_by_id(account_id)
    if account is None or account.user_id != db_user.id:
        await callback.answer("Кабинет не найден", show_alert=True)
        return
    await state.update_data(rotate_account_id=account_id)
    if account.marketplace == Marketplace.WB:
        await state.set_state(RotateWbKeyStates.waiting_api_key)
        prompt = "<b>Wildberries</b>\n\nПришлите новый ключ (категория «Вопросы и отзывы»)."
    else:
        await state.set_state(RotateOzonKeyStates.waiting_client_id)
        prompt = "<b>Ozon</b>\n\nПришлите новый <b>Client-Id</b>."
    await callback.answer()
    if callback.message:
        await safe_edit_message(
            callback.message,prompt)


@router.message(RotateWbKeyStates.waiting_api_key, F.text)
async def rotate_wb_key_finish(message: Message, state: FSMContext, db_user: DbUser) -> None:
    key = (message.text or "").strip()
    if len(key) < 10:
        await message.answer("Ключ слишком короткий.")
        return
    data = await state.get_data()
    account_id = int(data.get("rotate_account_id", 0))
    session_factory = get_session_factory()
    try:
        async with session_factory() as session:
            account = await AccountRepository(session).get_by_id(account_id)
            if account is None or account.user_id != db_user.id:
                await message.answer("Кабинет не найден.", reply_markup=settings_menu_keyboard())
                await state.clear()
                return
            await test_and_update_wb_api_key(session, account, api_key=key)
            await session.commit()
    except EncryptionError:
        await message.answer("FERNET_KEY не настроен.", reply_markup=settings_menu_keyboard())
        await state.clear()
        return
    except MarketplaceAPIError as exc:
        await message.answer(f"Ключ не принят:\n\n{exc}", reply_markup=settings_menu_keyboard())
        return
    await state.clear()
    await message.answer(
        f"✅ Ключ WB обновлён (кабинет #{account_id}). Кабинет снова активен.",
        reply_markup=settings_menu_keyboard(),
    )


@router.message(RotateOzonKeyStates.waiting_client_id, F.text)
async def rotate_ozon_client_id(message: Message, state: FSMContext) -> None:
    client_id = (message.text or "").strip()
    if not client_id.isdigit():
        await message.answer("Client-Id обычно числовой.")
        return
    await state.update_data(rotate_ozon_client_id=client_id)
    await state.set_state(RotateOzonKeyStates.waiting_api_key)
    await message.answer("Теперь пришлите новый <b>Api-Key</b> Ozon.")


@router.message(RotateOzonKeyStates.waiting_api_key, F.text)
async def rotate_ozon_key_finish(message: Message, state: FSMContext, db_user: DbUser) -> None:
    api_key = (message.text or "").strip()
    if len(api_key) < 8:
        await message.answer("Api-Key слишком короткий.")
        return
    data = await state.get_data()
    account_id = int(data.get("rotate_account_id", 0))
    client_id = data.get("rotate_ozon_client_id")
    if not client_id:
        await state.clear()
        await message.answer("Сессия сброшена.")
        return
    session_factory = get_session_factory()
    try:
        async with session_factory() as session:
            account = await AccountRepository(session).get_by_id(account_id)
            if account is None or account.user_id != db_user.id:
                await message.answer("Кабинет не найден.", reply_markup=settings_menu_keyboard())
                await state.clear()
                return
            await test_and_update_ozon_credentials(
                session,
                account,
                client_id=str(client_id),
                api_key=api_key,
            )
            await session.commit()
    except EncryptionError:
        await message.answer("FERNET_KEY не настроен.", reply_markup=settings_menu_keyboard())
        await state.clear()
        return
    except MarketplaceAPIError as exc:
        await message.answer(f"Ключи не приняты:\n\n{exc}", reply_markup=settings_menu_keyboard())
        return
    await state.clear()
    await message.answer(
        f"✅ Ключи Ozon обновлены (кабинет #{account_id}). Кабинет снова активен.",
        reply_markup=settings_menu_keyboard(),
    )


@router.callback_query(F.data == "settings:tone")
async def settings_tone_list(callback: CallbackQuery, db_user: DbUser) -> None:
    session_factory = get_session_factory()
    async with session_factory() as session:
        profiles = await ToneProfileRepository(session).list_by_user_id(db_user.id)
        lite_plus = await has_lite_or_higher(session, db_user.id)
        tone_count = await count_user_tone_profiles(session, db_user.id)
    await callback.answer()
    if lite_plus:
        limit_line = "Можно создать несколько профилей тона ответа."
    else:
        limit_line = (
            f"Бесплатно: <b>{tone_count}/{FREE_MAX_TONE_PROFILES}</b> профиль. "
            "Lite/PRO — без лимита."
        )
    if callback.message:
        await safe_edit_message(
            callback.message,
            f"<b>Тон ответа</b>\n\n{limit_line}",
            reply_markup=tone_menu_keyboard(profiles),
        )


@router.callback_query(F.data == "settings:tone:add")
async def settings_tone_add(callback: CallbackQuery, state: FSMContext, db_user: DbUser) -> None:
    session_factory = get_session_factory()
    async with session_factory() as session:
        allowed, msg = await can_add_tone_profile(session, db_user.id)
    if not allowed:
        await callback.answer(msg or "Лимит профилей тона", show_alert=True)
        return
    await state.set_state(ToneProfileStates.waiting_description)
    await callback.answer()
    if callback.message:
        await bind_ui_message(state, callback.message)
        await safe_edit_message(
            callback.message,
            "Опишите желаемый тон ответов (1–3 предложения), например: "
            "«Вежливо, без канцелярита, с благодарностью за отзыв»."
        )


@router.message(ToneProfileStates.waiting_description, F.text)
async def settings_tone_description(message: Message, state: FSMContext) -> None:
    desc = (message.text or "").strip()
    if len(desc) < 5:
        await edit_bound_ui_message(
            message,
            state,
            "Описание слишком короткое. Напишите хотя бы 5 символов.",
            delete_user_message=True,
        )
        return
    await state.update_data(tone_description=desc)
    await state.set_state(ToneProfileStates.waiting_examples)
    await edit_bound_ui_message(
        message,
        state,
        "Пришлите 1–3 примера ваших ответов (каждый с новой строки) или «-» без примеров.",
        delete_user_message=True,
    )


@router.message(ToneProfileStates.waiting_examples, F.text)
async def settings_tone_examples(message: Message, state: FSMContext, db_user: DbUser) -> None:
    data = await state.get_data()
    desc = data.get("tone_description")
    if not desc:
        await state.clear()
        await edit_bound_ui_message(message, state, "Сессия сброшена.", reply_markup=settings_menu_keyboard())
        return
    raw = (message.text or "").strip()
    examples: list[str] | None = None
    if raw not in {"", "-", "—"}:
        examples = [line.strip() for line in raw.splitlines() if line.strip()][:3]

    session_factory = get_session_factory()
    async with session_factory() as session:
        allowed, limit_msg = await can_add_tone_profile(session, db_user.id)
        if not allowed:
            await state.clear()
            await edit_bound_ui_message(
                message,
                state,
                limit_msg or "Лимит профилей тона.",
                reply_markup=settings_menu_keyboard(),
                delete_user_message=True,
            )
            return
        profile = await ToneProfileRepository(session).create(
            user_id=db_user.id,
            description=str(desc),
            example_replies=examples,
        )
        user = await UserRepository(session).get_by_id(db_user.id)
        finished = bool(user and await try_complete_onboarding(session, user))
        await session.commit()

    await state.clear()
    if finished:
        done_text, done_kb = onboarding_finished_screen()
        await edit_bound_ui_message(message, state, done_text, reply_markup=done_kb, delete_user_message=True)
    else:
        await edit_bound_ui_message(
            message,
            state,
            f"✅ Профиль тона #{profile.id} сохранён.",
            reply_markup=settings_menu_keyboard(),
            delete_user_message=True,
        )


@router.callback_query(F.data.startswith("settings:tone:view:"))
async def settings_tone_view(callback: CallbackQuery, db_user: DbUser) -> None:
    profile_id = int(callback.data.split(":")[-1])
    session_factory = get_session_factory()
    async with session_factory() as session:
        profile = await ToneProfileRepository(session).get_by_id(profile_id)
    if profile is None or profile.user_id != db_user.id:
        await callback.answer("Не найден", show_alert=True)
        return
    examples = profile.example_replies or []
    ex_text = "\n".join(f"• {item}" for item in examples) if examples else "—"
    await callback.answer()
    if callback.message:
        await safe_edit_message(
            callback.message,
            f"<b>Профиль #{profile.id}</b>\n\n{profile.description}\n\n<b>Примеры:</b>\n{ex_text}",
            reply_markup=tone_detail_keyboard(profile.id, profile.is_default),
        )


@router.callback_query(F.data.startswith("settings:tone:default:"))
async def settings_tone_set_default(callback: CallbackQuery, db_user: DbUser) -> None:
    profile_id = int(callback.data.split(":")[-1])
    session_factory = get_session_factory()
    async with session_factory() as session:
        profile = await ToneProfileRepository(session).set_default(profile_id, db_user.id)
        await session.commit()
    if profile is None:
        await callback.answer("Не найден", show_alert=True)
        return
    await callback.answer("Профиль по умолчанию обновлён")
    if callback.message:
        examples = profile.example_replies or []
        ex_text = "\n".join(f"• {item}" for item in examples) if examples else "—"
        await safe_edit_message(
            callback.message,
            f"<b>Профиль #{profile.id}</b> ★\n\n{profile.description}\n\n<b>Примеры:</b>\n{ex_text}",
            reply_markup=tone_detail_keyboard(profile.id, True),
        )


@router.callback_query(F.data.startswith("settings:tone:edit:"))
async def settings_tone_edit_start(callback: CallbackQuery, state: FSMContext, db_user: DbUser) -> None:
    profile_id = int(callback.data.split(":")[-1])
    session_factory = get_session_factory()
    async with session_factory() as session:
        profile = await ToneProfileRepository(session).get_by_id(profile_id)
    if profile is None or profile.user_id != db_user.id:
        await callback.answer("Не найден", show_alert=True)
        return
    await state.update_data(editing_profile_id=profile_id)
    await state.set_state(ToneProfileStates.waiting_edit_description)
    await callback.answer()
    if callback.message:
        await bind_ui_message(state, callback.message)
        await safe_edit_message(
            callback.message,
            f"Новое описание тона для профиля #{profile_id}:\n\n"
            f"Текущее: {profile.description}"
        )


@router.message(ToneProfileStates.waiting_edit_description, F.text)
async def settings_tone_edit_description(message: Message, state: FSMContext) -> None:
    desc = (message.text or "").strip()
    if len(desc) < 5:
        await edit_bound_ui_message(message, state, "Слишком коротко.", delete_user_message=True)
        return
    await state.update_data(tone_description=desc)
    await state.set_state(ToneProfileStates.waiting_edit_examples)
    await edit_bound_ui_message(
        message,
        state,
        "Примеры ответов (строки) или «-» оставить без изменений примеров.",
        delete_user_message=True,
    )


@router.message(ToneProfileStates.waiting_edit_examples, F.text)
async def settings_tone_edit_finish(message: Message, state: FSMContext, db_user: DbUser) -> None:
    data = await state.get_data()
    profile_id = data.get("editing_profile_id")
    desc = data.get("tone_description")
    if not profile_id or not desc:
        await state.clear()
        await edit_bound_ui_message(message, state, "Сессия сброшена.")
        return
    raw = (message.text or "").strip()
    examples: list[str] | None | str = None
    if raw not in {"", "-", "—"}:
        examples = [line.strip() for line in raw.splitlines() if line.strip()][:3]

    session_factory = get_session_factory()
    async with session_factory() as session:
        repo = ToneProfileRepository(session)
        if examples is None:
            old = await repo.get_by_id(int(profile_id))
            examples = old.example_replies if old else None
        profile = await repo.update_description(
            int(profile_id),
            db_user.id,
            description=str(desc),
            example_replies=examples if isinstance(examples, list) else None,
        )
        await session.commit()
    await state.clear()
    if profile is None:
        await edit_bound_ui_message(message, state, "Не удалось сохранить.", delete_user_message=True)
        return
    await edit_bound_ui_message(
        message,
        state,
        f"✅ Профиль #{profile.id} обновлён.",
        reply_markup=settings_menu_keyboard(),
        delete_user_message=True,
    )


def _profile_keyboard(user) -> InlineKeyboardMarkup:
    tz = user.ui_timezone or "Europe/Minsk"
    tz_label = "Минск (UTC+3)" if "Minsk" in tz else "Москва (UTC+3)"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"🕐 Часовой пояс: {tz_label}", callback_data="settings:profile:tz")],
            [InlineKeyboardButton(text="🌐 Язык: русский", callback_data="settings:profile:lang")],
            [InlineKeyboardButton(text="◀️ Настройки", callback_data="menu:settings")],
        ]
    )


@router.callback_query(F.data == "settings:profile")
async def settings_profile(callback: CallbackQuery, db_user: DbUser) -> None:
    session_factory = get_session_factory()
    async with session_factory() as session:
        user = await UserRepository(session).get_by_id(db_user.id)
    if user is None:
        await callback.answer("Ошибка")
        return
    await callback.answer()
    if callback.message:
        await safe_edit_message(
            callback.message,
            "👤 <b>Профиль</b>\n\n"
            f"Telegram ID: <code>{user.tg_id}</code>\n"
            f"Часовой пояс UI: <b>{user.ui_timezone}</b>\n"
            f"Язык: <b>{user.ui_language}</b>",
            reply_markup=_profile_keyboard(user),
        )


@router.callback_query(F.data == "settings:profile:tz")
async def settings_profile_tz_toggle(callback: CallbackQuery, db_user: DbUser) -> None:
    session_factory = get_session_factory()
    async with session_factory() as session:
        user = await UserRepository(session).get_by_id(db_user.id)
        if user is None:
            return
        new_tz = "Europe/Moscow" if "Minsk" in (user.ui_timezone or "") else "Europe/Minsk"
        await UserRepository(session).set_ui_prefs(db_user.id, ui_timezone=new_tz)
        await session.commit()
        user = await UserRepository(session).get_by_id(db_user.id)
    await callback.answer("Сохранено")
    if callback.message and user:
        await safe_edit_message(
            callback.message,
            "👤 <b>Профиль</b>\n\n"
            f"Telegram ID: <code>{user.tg_id}</code>\n"
            f"Часовой пояс UI: <b>{user.ui_timezone}</b>\n"
            f"Язык: <b>{user.ui_language}</b>",
            reply_markup=_profile_keyboard(user),
        )


@router.callback_query(F.data == "settings:profile:lang")
async def settings_profile_lang(callback: CallbackQuery) -> None:
    await callback.answer("Пока доступен только русский интерфейс.", show_alert=True)


@router.callback_query(F.data == "settings:notifications")
async def settings_notifications(callback: CallbackQuery, db_user: DbUser) -> None:
    from app.bot.keyboards.notifications import notifications_keyboard

    session_factory = get_session_factory()
    async with session_factory() as session:
        user = await UserRepository(session).get_by_id(db_user.id)
    if user is None:
        await callback.answer("Ошибка")
        return
    await callback.answer()
    if callback.message:
        await safe_edit_message(
            callback.message,
            _notifications_screen_text(),
            reply_markup=notifications_keyboard(
                notify_new=user.notify_new_reviews,
                negative_only=user.notify_negative_only,
                daily_digest=user.notify_daily_digest,
                notify_stale=user.notify_stale_reviews,
                notify_questions=user.notify_buyer_questions,
                soft_recommend=user.soft_product_recommend,
            ),
        )


@router.callback_query(F.data == "settings:notify:toggle_new")
async def settings_notify_toggle_new(callback: CallbackQuery, db_user: DbUser) -> None:
    from app.bot.keyboards.notifications import notifications_keyboard

    session_factory = get_session_factory()
    async with session_factory() as session:
        user = await UserRepository(session).get_by_id(db_user.id)
        if user is None:
            return
        new_val = not user.notify_new_reviews
        await UserRepository(session).set_notification_prefs(
            db_user.id,
            notify_new_reviews=new_val,
        )
        await session.commit()
        user = await UserRepository(session).get_by_id(db_user.id)
    await callback.answer("Сохранено")
    if callback.message and user:
        preview = preview_new_reviews(negative_only=user.notify_negative_only) if new_val else None
        await safe_edit_message(
            callback.message,
            _notifications_screen_text(preview_block=preview),
            reply_markup=notifications_keyboard(
                notify_new=user.notify_new_reviews,
                negative_only=user.notify_negative_only,
                daily_digest=user.notify_daily_digest,
                notify_stale=user.notify_stale_reviews,
                notify_questions=user.notify_buyer_questions,
                soft_recommend=user.soft_product_recommend,
            ),
        )


@router.callback_query(F.data == "settings:notify:toggle_negative")
async def settings_notify_toggle_negative(callback: CallbackQuery, db_user: DbUser) -> None:
    from app.bot.keyboards.notifications import notifications_keyboard

    session_factory = get_session_factory()
    async with session_factory() as session:
        user = await UserRepository(session).get_by_id(db_user.id)
        if user is None:
            return
        await UserRepository(session).set_notification_prefs(
            db_user.id,
            notify_negative_only=not user.notify_negative_only,
        )
        await session.commit()
        user = await UserRepository(session).get_by_id(db_user.id)
    await callback.answer("Сохранено")
    if callback.message and user:
        await safe_edit_message(
            callback.message,
            _notifications_screen_text(),
            reply_markup=notifications_keyboard(
                notify_new=user.notify_new_reviews,
                negative_only=user.notify_negative_only,
                daily_digest=user.notify_daily_digest,
                notify_stale=user.notify_stale_reviews,
                notify_questions=user.notify_buyer_questions,
                soft_recommend=user.soft_product_recommend,
            ),
        )


@router.callback_query(F.data == "settings:notify:toggle_questions")
async def settings_notify_toggle_questions(callback: CallbackQuery, db_user: DbUser) -> None:
    from app.bot.keyboards.notifications import notifications_keyboard

    session_factory = get_session_factory()
    async with session_factory() as session:
        user = await UserRepository(session).get_by_id(db_user.id)
        if user is None:
            return
        new_val = not user.notify_buyer_questions
        await UserRepository(session).set_notification_prefs(
            db_user.id,
            notify_buyer_questions=new_val,
        )
        await session.commit()
        user = await UserRepository(session).get_by_id(db_user.id)
    await callback.answer("Сохранено")
    if callback.message and user is not None:
        preview = preview_buyer_questions() if new_val else None
        await safe_edit_message(
            callback.message,
            _notifications_screen_text(preview_block=preview),
            reply_markup=notifications_keyboard(
                notify_new=user.notify_new_reviews,
                negative_only=user.notify_negative_only,
                daily_digest=user.notify_daily_digest,
                notify_stale=user.notify_stale_reviews,
                notify_questions=user.notify_buyer_questions,
                soft_recommend=user.soft_product_recommend,
            ),
        )


@router.callback_query(F.data == "settings:notify:toggle_digest")
async def settings_notify_toggle_digest(callback: CallbackQuery, db_user: DbUser) -> None:
    from app.bot.keyboards.notifications import notifications_keyboard

    session_factory = get_session_factory()
    async with session_factory() as session:
        user = await UserRepository(session).get_by_id(db_user.id)
        if user is None:
            return
        new_val = not user.notify_daily_digest
        await UserRepository(session).set_notification_prefs(
            db_user.id,
            notify_daily_digest=new_val,
        )
        await session.commit()
        user = await UserRepository(session).get_by_id(db_user.id)
    await callback.answer("Сохранено")
    if callback.message and user:
        preview = preview_daily_digest() if new_val else None
        await safe_edit_message(
            callback.message,
            _notifications_screen_text(preview_block=preview),
            reply_markup=notifications_keyboard(
                notify_new=user.notify_new_reviews,
                negative_only=user.notify_negative_only,
                daily_digest=user.notify_daily_digest,
                notify_stale=user.notify_stale_reviews,
                notify_questions=user.notify_buyer_questions,
                soft_recommend=user.soft_product_recommend,
            ),
        )


@router.callback_query(F.data == "settings:notify:toggle_stale")
async def settings_notify_toggle_stale(callback: CallbackQuery, db_user: DbUser) -> None:
    from app.bot.keyboards.notifications import notifications_keyboard

    session_factory = get_session_factory()
    async with session_factory() as session:
        user = await UserRepository(session).get_by_id(db_user.id)
        if user is None:
            return
        new_val = not user.notify_stale_reviews
        await UserRepository(session).set_notification_prefs(
            db_user.id,
            notify_stale_reviews=new_val,
        )
        await session.commit()
        user = await UserRepository(session).get_by_id(db_user.id)
    await callback.answer("Сохранено")
    if callback.message and user:
        preview = preview_stale_reviews() if new_val else None
        await safe_edit_message(
            callback.message,
            _notifications_screen_text(preview_block=preview),
            reply_markup=notifications_keyboard(
                notify_new=user.notify_new_reviews,
                negative_only=user.notify_negative_only,
                daily_digest=user.notify_daily_digest,
                notify_stale=user.notify_stale_reviews,
                notify_questions=user.notify_buyer_questions,
                soft_recommend=user.soft_product_recommend,
            ),
        )


@router.callback_query(F.data == "settings:notify:toggle_recommend")
async def settings_notify_toggle_recommend(callback: CallbackQuery, db_user: DbUser) -> None:
    from app.bot.keyboards.notifications import notifications_keyboard

    session_factory = get_session_factory()
    async with session_factory() as session:
        user = await UserRepository(session).get_by_id(db_user.id)
        if user is None:
            return
        await UserRepository(session).set_notification_prefs(
            db_user.id,
            soft_product_recommend=not user.soft_product_recommend,
        )
        await session.commit()
        user = await UserRepository(session).get_by_id(db_user.id)
    await callback.answer("Сохранено")
    if callback.message and user:
        await safe_edit_message(
            callback.message,
            _notifications_screen_text(),
            reply_markup=notifications_keyboard(
                notify_new=user.notify_new_reviews,
                negative_only=user.notify_negative_only,
                daily_digest=user.notify_daily_digest,
                notify_stale=user.notify_stale_reviews,
                notify_questions=user.notify_buyer_questions,
                soft_recommend=user.soft_product_recommend,
            ),
        )


@router.callback_query(F.data.regexp(r"^settings:account_sync:\d+$"))
async def settings_account_sync(callback: CallbackQuery, db_user: DbUser) -> None:
    account_id = int(callback.data.split(":")[-1])
    session_factory = get_session_factory()
    async with session_factory() as session:
        account = await AccountRepository(session).get_by_id(account_id)
        if account is None or account.user_id != db_user.id:
            await callback.answer("Кабинет не найден", show_alert=True)
            return
        try:
            created, _, _ = await sync_account_reviews(session, account)
            await session.commit()
            msg = f"✅ Обновление готово. Новых отзывов: <b>{created}</b>."
        except MarketplaceAPIError as exc:
            await session.commit()
            msg = f"⚠️ Sync не удался:\n{exc}"
        except Exception as exc:
            from app.bot.user_errors import user_error_from_exception

            await session.commit()
            facing = user_error_from_exception(exc)
            msg = facing.html
            kb = facing.reply_markup
            await callback.answer("Готово")
            if callback.message:
                await safe_edit_message(callback.message, msg, reply_markup=kb)
            return
    await callback.answer("Готово")
    if callback.message:
        from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="🩺 Здоровье", callback_data="menu:service_status"),
                    InlineKeyboardButton(text="⚙️ Настройки", callback_data="menu:settings"),
                ],
            ]
        )
        await safe_edit_message(callback.message, msg, reply_markup=kb)


@router.callback_query(F.data == "settings:templates")
async def settings_templates_menu(callback: CallbackQuery, db_user: DbUser) -> None:
    from app.bot.keyboards.templates import templates_menu_keyboard

    session_factory = get_session_factory()
    async with session_factory() as session:
        user = await UserRepository(session).get_by_id(db_user.id)
        templates = list_templates(user) if user else []
    lines = ["📝 <b>Мои шаблоны</b>", "", "До 5 фраз — кнопки на экране вариантов ответа.", ""]
    if templates:
        for tpl in templates:
            lines.append(f"• <b>{tpl['label']}</b>: {tpl['text'][:80]}…" if len(tpl["text"]) > 80 else f"• <b>{tpl['label']}</b>: {tpl['text']}")
    else:
        lines.append("<i>Пока пусто — добавьте первый шаблон.</i>")
    await callback.answer()
    if callback.message:
        await safe_edit_message(
            callback.message,
            "\n".join(lines),
            reply_markup=templates_menu_keyboard(templates),
        )


@router.callback_query(F.data == "settings:tpl:add")
async def settings_tpl_add_start(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(ReplyTemplateStates.waiting_label)
    await callback.answer()
    if callback.message:
        await safe_edit_message(
            callback.message,
            "📝 Новый шаблон\n\nПришлите <b>короткое название</b> кнопки (до 24 символов):"
        )


@router.message(ReplyTemplateStates.waiting_label, F.text)
async def settings_tpl_add_label(message: Message, state: FSMContext) -> None:
    label = (message.text or "").strip()[:24]
    if len(label) < 2:
        await message.answer("Название слишком короткое.")
        return
    await state.update_data(tpl_label=label)
    await state.set_state(ReplyTemplateStates.waiting_text)
    await message.answer("Теперь пришлите <b>текст ответа</b> одним сообщением:")


@router.message(ReplyTemplateStates.waiting_text, F.text)
async def settings_tpl_add_text(message: Message, state: FSMContext, db_user: DbUser) -> None:
    from app.bot.keyboards.templates import templates_menu_keyboard

    data = await state.get_data()
    label = str(data.get("tpl_label") or "Шаблон")
    text = (message.text or "").strip()
    session_factory = get_session_factory()
    async with session_factory() as session:
        user = await UserRepository(session).get_by_id(db_user.id)
        if user is None:
            await state.clear()
            return
        ok, err = add_template(user, label=label, text=text)
        await session.commit()
        templates = list_templates(user)
    await state.clear()
    if not ok:
        await message.answer(err or "Не удалось сохранить.", reply_markup=settings_menu_keyboard())
        return
    await message.answer("✅ Шаблон сохранён.", reply_markup=templates_menu_keyboard(templates))


@router.callback_query(F.data.startswith("settings:tpl:del:"))
async def settings_tpl_delete(callback: CallbackQuery, db_user: DbUser) -> None:
    from app.bot.keyboards.templates import templates_menu_keyboard

    template_id = callback.data.split(":")[-1]
    session_factory = get_session_factory()
    async with session_factory() as session:
        user = await UserRepository(session).get_by_id(db_user.id)
        if user is None:
            return
        remove_template(user, template_id)
        await session.commit()
        templates = list_templates(user)
    await callback.answer("Удалено")
    if callback.message:
        await safe_edit_message(
            callback.message,
            "📝 <b>Мои шаблоны</b>",
            reply_markup=templates_menu_keyboard(templates),
        )


@router.callback_query(F.data.startswith("settings:tone:delete:"))
async def settings_tone_delete(callback: CallbackQuery, db_user: DbUser) -> None:
    profile_id = int(callback.data.split(":")[-1])
    session_factory = get_session_factory()
    async with session_factory() as session:
        deleted = await ToneProfileRepository(session).delete(profile_id, db_user.id)
        profiles = await ToneProfileRepository(session).list_by_user_id(db_user.id)
        await session.commit()
    await callback.answer("Удалено" if deleted else "Не найден")
    if callback.message:
        await safe_edit_message(
            callback.message,
            "<b>Тон ответа</b>",
            reply_markup=tone_menu_keyboard(profiles),
        )
