from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.bot.keyboards.menu import main_menu_keyboard
from app.bot.keyboards.settings import (
    account_detail_keyboard,
    accounts_menu_keyboard,
    settings_menu_keyboard,
    tone_detail_keyboard,
    tone_menu_keyboard,
)
from app.bot.states.settings import ConnectOzonStates, ConnectWbStates, ToneProfileStates
from app.core.security import EncryptionError
from app.db.models import Marketplace, User as DbUser
from app.db.repositories.account import AccountRepository
from app.db.repositories.tone_profile import ToneProfileRepository
from app.db.session import get_session_factory
from app.services.marketplace.account_connect import test_and_create_ozon_account, test_and_create_wb_account
from app.services.marketplace.base import MarketplaceAPIError

router = Router(name="settings")

SETTINGS_TEXT = (
    "<b>Настройки</b>\n\n"
    "Подключите API маркетплейсов, настройте tone of voice и (PRO) авто-публикацию."
)


@router.callback_query(F.data == "menu:settings")
async def menu_settings(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.answer()
    if callback.message:
        await callback.message.edit_text(SETTINGS_TEXT, reply_markup=settings_menu_keyboard())


@router.callback_query(F.data == "pro:autopublish")
async def pro_autopublish_stub(callback: CallbackQuery) -> None:
    await callback.answer()
    if callback.message:
        await callback.message.edit_text(
            "<b>Авто-публикация (PRO)</b>\n\n"
            "Фоновый poller уже подтягивает новые отзывы. "
            "Полная авто-публикация без подтверждения — в следующих итерациях.",
            reply_markup=settings_menu_keyboard(),
        )


@router.callback_query(F.data == "settings:accounts")
async def settings_accounts(callback: CallbackQuery, db_user: DbUser) -> None:
    session_factory = get_session_factory()
    async with session_factory() as session:
        accounts = await AccountRepository(session).list_by_user_id(db_user.id)
    await callback.answer()
    text = (
        "<b>Кабинеты маркетплейсов</b>\n\n"
        "Можно подключить несколько аккаунтов WB/Ozon."
    )
    if callback.message:
        await callback.message.edit_text(text, reply_markup=accounts_menu_keyboard(accounts))


@router.callback_query(F.data == "settings:connect:wb")
async def connect_wb_start(callback: CallbackQuery, state: FSMContext) -> None:
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
async def connect_ozon_start(callback: CallbackQuery, state: FSMContext) -> None:
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
    if account is None or account.user_id != db_user.id:
        await callback.answer("Кабинет не найден", show_alert=True)
        return
    mp = "Wildberries" if account.marketplace == Marketplace.WB else "Ozon"
    name = account.shop_name or f"{mp} #{account.id}"
    await callback.answer()
    if callback.message:
        await callback.message.edit_text(
            f"<b>{name}</b>\nПлощадка: {mp}\nСтатус: {'активен' if account.is_active else 'отключён'}",
            reply_markup=account_detail_keyboard(account.id, account.is_active),
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
        await callback.message.edit_text(
            f"<b>{name}</b>\nПлощадка: {mp}\nСтатус: {'активен' if account.is_active else 'отключён'}",
            reply_markup=account_detail_keyboard(account.id, account.is_active),
        )


@router.callback_query(F.data == "settings:tone")
async def settings_tone_list(callback: CallbackQuery, db_user: DbUser) -> None:
    session_factory = get_session_factory()
    async with session_factory() as session:
        profiles = await ToneProfileRepository(session).list_by_user_id(db_user.id)
    await callback.answer()
    if callback.message:
        await callback.message.edit_text(
            "<b>Tone of voice</b>\n\nПрофили используются при генерации ответов.",
            reply_markup=tone_menu_keyboard(profiles),
        )


@router.callback_query(F.data == "settings:tone:add")
async def settings_tone_add(callback: CallbackQuery, state: FSMContext) -> None:
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
            reply_markup=tone_detail_keyboard(profile.id),
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
