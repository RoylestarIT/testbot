from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.bot.copy import SETTINGS_INTRO as SETTINGS_TEXT
from app.bot.keyboards.menu import main_menu_keyboard
from app.bot.keyboards.settings import (
    account_detail_keyboard,
    accounts_menu_keyboard,
    autopublish_accounts_keyboard,
    settings_menu_keyboard,
    tone_detail_keyboard,
    tone_menu_keyboard,
)
from app.bot.states.settings import ConnectOzonStates, ConnectWbStates, ReplyTemplateStates, ToneProfileStates
from app.core.security import EncryptionError
from app.db.models import Marketplace, User as DbUser
from app.db.repositories.account import AccountRepository
from app.db.repositories.user import UserRepository
from app.db.repositories.tone_profile import ToneProfileRepository
from app.db.session import get_session_factory
from app.services.marketplace.account_connect import test_and_create_ozon_account, test_and_create_wb_account
from app.services.marketplace.sync_service import sync_account_reviews
from app.services.reply_templates import add_template, list_templates, remove_template
from app.services.generation_limit import is_pro_user
from app.services.marketplace.base import MarketplaceAPIError
from app.services.plans import (
    FREE_MAX_MARKETPLACE_ACCOUNTS,
    FREE_MAX_TONE_PROFILES,
    can_add_marketplace_account,
    can_add_tone_profile,
    count_user_api_accounts,
    count_user_tone_profiles,
    has_lite_or_higher,
)

router = Router(name="settings")


@router.callback_query(F.data == "menu:settings")
async def menu_settings(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.answer()
    if callback.message:
        await callback.message.edit_text(SETTINGS_TEXT, reply_markup=settings_menu_keyboard())


@router.callback_query(F.data == "pro:autopublish")
async def pro_autopublish_menu(callback: CallbackQuery, db_user: DbUser) -> None:
    session_factory = get_session_factory()
    async with session_factory() as session:
        accounts = await AccountRepository(session).list_by_user_id(db_user.id, active_only=True)
    await callback.answer()
    if callback.message:
        await callback.message.edit_text(
            "<b>Авто-публикация (PRO)</b>\n\n"
            "Для отзывов <b>4–5★</b> бот сгенерирует и опубликует ответ без подтверждения "
            "(1–3★ — только уведомление). Выберите кабинет:",
            reply_markup=autopublish_accounts_keyboard(accounts),
        )


@router.callback_query(F.data == "settings:accounts")
async def settings_accounts(callback: CallbackQuery, db_user: DbUser) -> None:
    session_factory = get_session_factory()
    async with session_factory() as session:
        accounts = await AccountRepository(session).list_by_user_id(db_user.id)
        lite_plus = await has_lite_or_higher(session, db_user.id)
        api_count = await count_user_api_accounts(session, db_user.id)
    await callback.answer()
    if lite_plus:
        limit_line = "Можно подключить несколько аккаунтов WB/Ozon."
    else:
        limit_line = (
            f"Бесплатно: <b>{api_count}/{FREE_MAX_MARKETPLACE_ACCOUNTS}</b> кабинет WB/Ozon. "
            "Lite/PRO — без лимита."
        )
    text = f"<b>Кабинеты маркетплейсов</b>\n\n{limit_line}"
    if callback.message:
        await callback.message.edit_text(text, reply_markup=accounts_menu_keyboard(accounts))


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
        await callback.message.edit_text(
            "<b>Wildberries</b>\n\n"
            "Пришлите API-ключ категории «Вопросы и отзывы» одним сообщением.\n"
            "Ключ будет зашифрован и сохранён в БД.",
        )


@router.message(ConnectWbStates.waiting_api_key, F.text)
async def connect_wb_api_key(message: Message, state: FSMContext) -> None:
    key = (message.text or "").strip()
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
            "На сервере не настроен FERNET_KEY — сохранение ключей невозможно.",
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
    hint = "Тестовый запрос выполнен, отзывов пока нет." if sample is None else "Получен 1 отзыв — ключ работает."
    await message.answer(
        f"✅ Wildberries подключён (кабинет #{account.id}).\n{hint}",
        reply_markup=settings_menu_keyboard(),
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
        await callback.message.edit_text(
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
    await message.answer(
        f"✅ Ozon подключён (кабинет #{account.id}).\n{hint}",
        reply_markup=settings_menu_keyboard(),
    )


@router.callback_query(F.data.startswith("settings:account:"))
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
        sync_hint = f"\n🔄 Sync: {account.last_sync_at.strftime('%d.%m.%Y %H:%M')} UTC"
    if account.last_sync_error:
        sync_hint += f"\n⚠️ {account.last_sync_error[:200]}"
    key_status = "✅ ключ OK" if account.is_active and not account.last_sync_error else "⚠️ проверьте ключ"
    await callback.answer()
    if callback.message:
        await callback.message.edit_text(
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
        accounts = await repo.list_by_user_id(db_user.id, active_only=True)
        await session.commit()
    await callback.answer("Сохранено")
    if callback.message and account is not None:
        await callback.message.edit_text(
            "<b>Авто-публикация (PRO)</b>\n\n"
            "4–5★ — авто-ответ; 1–3★ — только уведомление.",
            reply_markup=autopublish_accounts_keyboard(accounts),
        )


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
        await callback.message.edit_text(
            f"<b>{name}</b>\nПлощадка: {mp}\nСтатус: {'активен' if account.is_active else 'отключён'}",
            reply_markup=account_detail_keyboard(
                account.id,
                account.is_active,
                auto_publish_enabled=account.auto_publish_enabled,
                show_auto_publish=is_pro and account.marketplace in (Marketplace.WB, Marketplace.OZON),
            ),
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
        limit_line = "Можно создать несколько профилей tone."
    else:
        limit_line = (
            f"Бесплатно: <b>{tone_count}/{FREE_MAX_TONE_PROFILES}</b> профиль. "
            "Lite/PRO — без лимита."
        )
    if callback.message:
        await callback.message.edit_text(
            f"<b>Tone of voice</b>\n\n{limit_line}",
            reply_markup=tone_menu_keyboard(profiles),
        )


@router.callback_query(F.data == "settings:tone:add")
async def settings_tone_add(callback: CallbackQuery, state: FSMContext, db_user: DbUser) -> None:
    session_factory = get_session_factory()
    async with session_factory() as session:
        allowed, msg = await can_add_tone_profile(session, db_user.id)
    if not allowed:
        await callback.answer(msg or "Лимит tone-профилей", show_alert=True)
        return
    await state.set_state(ToneProfileStates.waiting_description)
    await callback.answer()
    if callback.message:
        await callback.message.edit_text(
            "Опишите желаемый тон ответов (1–3 предложения), например: "
            "«Вежливо, без канцелярита, с благодарностью за отзыв»."
        )


@router.message(ToneProfileStates.waiting_description, F.text)
async def settings_tone_description(message: Message, state: FSMContext) -> None:
    desc = (message.text or "").strip()
    if len(desc) < 5:
        await message.answer("Описание слишком короткое.")
        return
    await state.update_data(tone_description=desc)
    await state.set_state(ToneProfileStates.waiting_examples)
    await message.answer(
        "Пришлите 1–3 примера ваших ответов (каждый с новой строки) или «-» без примеров."
    )


@router.message(ToneProfileStates.waiting_examples, F.text)
async def settings_tone_examples(message: Message, state: FSMContext, db_user: DbUser) -> None:
    data = await state.get_data()
    desc = data.get("tone_description")
    if not desc:
        await state.clear()
        await message.answer("Сессия сброшена.")
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
            await message.answer(limit_msg or "Лимит tone-профилей.", reply_markup=settings_menu_keyboard())
            return
        profile = await ToneProfileRepository(session).create(
            user_id=db_user.id,
            description=str(desc),
            example_replies=examples,
        )
        await session.commit()

    await state.clear()
    await message.answer(
        f"✅ Профиль tone #{profile.id} сохранён.",
        reply_markup=settings_menu_keyboard(),
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
        await callback.message.edit_text(
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
        await callback.message.edit_text(
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
        await callback.message.edit_text(
            f"Новое описание tone для профиля #{profile_id}:\n\n"
            f"Текущее: {profile.description}"
        )


@router.message(ToneProfileStates.waiting_edit_description, F.text)
async def settings_tone_edit_description(message: Message, state: FSMContext) -> None:
    desc = (message.text or "").strip()
    if len(desc) < 5:
        await message.answer("Слишком коротко.")
        return
    await state.update_data(tone_description=desc)
    await state.set_state(ToneProfileStates.waiting_edit_examples)
    await message.answer("Примеры ответов (строки) или «-» оставить без изменений примеров.")


@router.message(ToneProfileStates.waiting_edit_examples, F.text)
async def settings_tone_edit_finish(message: Message, state: FSMContext, db_user: DbUser) -> None:
    data = await state.get_data()
    profile_id = data.get("editing_profile_id")
    desc = data.get("tone_description")
    if not profile_id or not desc:
        await state.clear()
        await message.answer("Сессия сброшена.")
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
        await message.answer("Не удалось сохранить.")
        return
    await message.answer(
        f"✅ Профиль #{profile.id} обновлён.",
        reply_markup=settings_menu_keyboard(),
    )


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
    text = (
        "🔔 <b>Уведомления</b>\n\n"
        "Push от фоновой синхронизации (poller).\n"
        "«Только негатив» — только 1–3★.\n"
        "«Утренний дайджест» — сводка раз в день (~9:00 Минск, UTC+3).\n"
        "«Напоминание об очереди» — если отзывы без ответа дольше 24 ч (~18:00 Минск)."
    )
    if callback.message:
        await callback.message.edit_text(
            text,
            reply_markup=notifications_keyboard(
                notify_new=user.notify_new_reviews,
                negative_only=user.notify_negative_only,
                daily_digest=user.notify_daily_digest,
                notify_stale=user.notify_stale_reviews,
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
        await UserRepository(session).set_notification_prefs(
            db_user.id,
            notify_new_reviews=not user.notify_new_reviews,
        )
        await session.commit()
        user = await UserRepository(session).get_by_id(db_user.id)
    await callback.answer("Сохранено")
    if callback.message and user:
        await callback.message.edit_text(
            "🔔 <b>Уведомления</b>",
            reply_markup=notifications_keyboard(
                notify_new=user.notify_new_reviews,
                negative_only=user.notify_negative_only,
                daily_digest=user.notify_daily_digest,
                notify_stale=user.notify_stale_reviews,
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
        await callback.message.edit_text(
            "🔔 <b>Уведомления</b>",
            reply_markup=notifications_keyboard(
                notify_new=user.notify_new_reviews,
                negative_only=user.notify_negative_only,
                daily_digest=user.notify_daily_digest,
                notify_stale=user.notify_stale_reviews,
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
        await UserRepository(session).set_notification_prefs(
            db_user.id,
            notify_daily_digest=not user.notify_daily_digest,
        )
        await session.commit()
        user = await UserRepository(session).get_by_id(db_user.id)
    await callback.answer("Сохранено")
    if callback.message and user:
        await callback.message.edit_text(
            "🔔 <b>Уведомления</b>",
            reply_markup=notifications_keyboard(
                notify_new=user.notify_new_reviews,
                negative_only=user.notify_negative_only,
                daily_digest=user.notify_daily_digest,
                notify_stale=user.notify_stale_reviews,
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
        await UserRepository(session).set_notification_prefs(
            db_user.id,
            notify_stale_reviews=not user.notify_stale_reviews,
        )
        await session.commit()
        user = await UserRepository(session).get_by_id(db_user.id)
    await callback.answer("Сохранено")
    if callback.message and user:
        await callback.message.edit_text(
            "🔔 <b>Уведомления</b>",
            reply_markup=notifications_keyboard(
                notify_new=user.notify_new_reviews,
                negative_only=user.notify_negative_only,
                daily_digest=user.notify_daily_digest,
                notify_stale=user.notify_stale_reviews,
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
            msg = f"✅ Sync готов. Новых отзывов: <b>{created}</b>."
        except MarketplaceAPIError as exc:
            await session.commit()
            msg = f"⚠️ Sync не удался:\n{exc}"
    await callback.answer("Готово")
    if callback.message:
        await callback.message.answer(msg, reply_markup=settings_menu_keyboard())


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
        await callback.message.edit_text(
            "\n".join(lines),
            reply_markup=templates_menu_keyboard(templates),
        )


@router.callback_query(F.data == "settings:tpl:add")
async def settings_tpl_add_start(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(ReplyTemplateStates.waiting_label)
    await callback.answer()
    if callback.message:
        await callback.message.edit_text(
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
        await callback.message.edit_text(
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
        await callback.message.edit_text(
            "<b>Tone of voice</b>",
            reply_markup=tone_menu_keyboard(profiles),
        )
