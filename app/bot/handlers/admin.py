from __future__ import annotations

import asyncio

from aiogram import Bot, F, Router
from aiogram.filters import Command, CommandObject
from aiogram.types import CallbackQuery, Message

from app.bot.keyboards.admin import admin_menu_keyboard, pending_subscription_keyboard
from app.bot.keyboards.menu import main_menu_keyboard
from app.core.config import get_settings
from app.db.models import SubscriptionPlan
from app.db.repositories.subscription import SubscriptionRepository
from app.db.repositories.user import UserRepository
from app.db.session import get_session_factory
from app.services.admin_stats import build_stats_message
from app.services.subscription import (
    approve_qr_subscription,
    grant_subscription_by_tg_id,
    plan_label,
    reject_qr_subscription,
)

router = Router(name="admin")

ADMIN_PANEL_TEXT = (
    "🛠 <b>Админ-панель ReviewPilot</b>\n\n"
    "Управление подписками и рассылками. Обычные пользователи этого меню не видят."
)

ADMIN_HELP = (
    "<b>Команды администратора</b>\n\n"
    "/admin — это меню\n"
    "/pending — заявки на оплату\n"
    "/approve &lt;id&gt; — подтвердить QR\n"
    "/reject &lt;id&gt; — отклонить QR\n"
    "/grant &lt;tg_id&gt; lite|pro — выдать подписку вручную\n"
    "/stats — статистика\n"
    "/broadcast preview … / send … — рассылка"
)


def _is_admin(telegram_id: int) -> bool:
    return telegram_id in get_settings().admin_ids


@router.message(Command("admin"))
async def cmd_admin(message: Message) -> None:
    if message.from_user is None or not _is_admin(message.from_user.id):
        await message.answer("Команда доступна только администраторам.")
        return
    await message.answer(ADMIN_PANEL_TEXT, reply_markup=admin_menu_keyboard())


@router.callback_query(F.data == "menu:admin")
async def menu_admin(callback: CallbackQuery) -> None:
    if callback.from_user is None or not _is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return
    await callback.answer()
    if callback.message:
        await callback.message.edit_text(ADMIN_PANEL_TEXT, reply_markup=admin_menu_keyboard())


@router.callback_query(F.data == "admin:stats")
async def admin_stats_callback(callback: CallbackQuery) -> None:
    if callback.from_user is None or not _is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return
    session_factory = get_session_factory()
    async with session_factory() as session:
        text = await build_stats_message(session)
    await callback.answer()
    if callback.message:
        await callback.message.edit_text(text, reply_markup=admin_menu_keyboard())


@router.callback_query(F.data == "admin:help")
async def admin_help_callback(callback: CallbackQuery) -> None:
    if callback.from_user is None or not _is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return
    await callback.answer()
    if callback.message:
        await callback.message.edit_text(ADMIN_HELP, reply_markup=admin_menu_keyboard())


@router.callback_query(F.data == "admin:pending")
async def admin_pending_callback(callback: CallbackQuery) -> None:
    if callback.from_user is None or not _is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return
    session_factory = get_session_factory()
    async with session_factory() as session:
        pending = await SubscriptionRepository(session).list_pending()
    await callback.answer()
    if callback.message:
        if not pending:
            await callback.message.edit_text(
                "⏳ <b>Pending</b>\n\nЗаявок нет.",
                reply_markup=admin_menu_keyboard(),
            )
            return
        sub = pending[0]
        async with session_factory() as session:
            user = await UserRepository(session).get_by_id(sub.user_id)
        tg = user.tg_id if user else "?"
        text = (
            f"⏳ <b>Pending</b> (1/{len(pending)})\n\n"
            f"ID: <code>{sub.id}</code>\n"
            f"User tg_id: <code>{tg}</code>\n"
            f"План: <b>{plan_label(sub.plan)}</b>\n"
            f"Метод: {sub.payment_method.value if sub.payment_method else '—'}"
        )
        await callback.message.edit_text(
            text,
            reply_markup=pending_subscription_keyboard(sub.id),
        )


@router.callback_query(F.data.startswith("admin:approve:"))
async def admin_approve_callback(callback: CallbackQuery, bot: Bot) -> None:
    if callback.from_user is None or not _is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return
    subscription_id = int(callback.data.split(":")[-1])
    session_factory = get_session_factory()
    async with session_factory() as session:
        subscription = await approve_qr_subscription(session, subscription_id)
        if subscription is None:
            await callback.answer("Не pending или не найдено", show_alert=True)
            return
        user = await UserRepository(session).get_by_id(subscription.user_id)
        await session.commit()
    await callback.answer("Активировано")
    if callback.message:
        await callback.message.edit_text(
            f"✅ Подписка #{subscription_id} активирована ({plan_label(subscription.plan)}).",
            reply_markup=admin_menu_keyboard(),
        )
    if user is not None:
        expires = subscription.expires_at.strftime("%d.%m.%Y") if subscription.expires_at else "—"
        try:
            await bot.send_message(
                user.tg_id,
                f"✅ Подписка активирована!\n\nТариф: <b>{plan_label(subscription.plan)}</b>\nДо: <b>{expires}</b>",
            )
        except Exception:
            pass


@router.callback_query(F.data.startswith("admin:reject:"))
async def admin_reject_callback(callback: CallbackQuery, bot: Bot) -> None:
    if callback.from_user is None or not _is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return
    subscription_id = int(callback.data.split(":")[-1])
    session_factory = get_session_factory()
    async with session_factory() as session:
        subscription = await reject_qr_subscription(session, subscription_id)
        if subscription is None:
            await callback.answer("Не найдено", show_alert=True)
            return
        user = await UserRepository(session).get_by_id(subscription.user_id)
        await session.commit()
    await callback.answer("Отклонено")
    if callback.message:
        await callback.message.edit_text(
            f"❌ Заявка #{subscription_id} отклонена.",
            reply_markup=admin_menu_keyboard(),
        )
    if user is not None:
        try:
            await bot.send_message(user.tg_id, "Заявка на оплату не подтверждена.")
        except Exception:
            pass


@router.message(Command("grant"))
async def grant_subscription(message: Message, command: CommandObject, bot: Bot) -> None:
    if message.from_user is None or not _is_admin(message.from_user.id):
        await message.answer("Команда доступна только администраторам.")
        return
    parts = (command.args or "").split()
    if len(parts) != 2 or not parts[0].isdigit():
        await message.answer("Использование: /grant <telegram_user_id> lite|pro")
        return
    tg_id = int(parts[0])
    plan_raw = parts[1].lower()
    plan = SubscriptionPlan.PRO if plan_raw == "pro" else SubscriptionPlan.LITE

    session_factory = get_session_factory()
    async with session_factory() as session:
        subscription, err = await grant_subscription_by_tg_id(session, tg_id=tg_id, plan=plan)
        if subscription is None:
            await message.answer(err or "Не удалось выдать подписку.")
            return
        await session.commit()

    await message.answer(
        f"✅ Выдана подписка {plan_label(plan)} пользователю <code>{tg_id}</code> "
        f"(subscription #{subscription.id})."
    )
    try:
        expires = subscription.expires_at.strftime("%d.%m.%Y") if subscription.expires_at else "—"
        await bot.send_message(
            tg_id,
            f"🎁 Вам активирован тариф <b>{plan_label(plan)}</b> администратором.\nДействует до: <b>{expires}</b>",
        )
    except Exception:
        await message.answer("Подписка в БД создана, но не удалось написать пользователю в Telegram.")


@router.message(Command("approve"))
async def approve_subscription(message: Message, command: CommandObject, bot: Bot) -> None:
    if message.from_user is None or not _is_admin(message.from_user.id):
        await message.answer("Команда доступна только администраторам.")
        return

    if not command.args or not command.args.strip().isdigit():
        await message.answer("Использование: /approve <subscription_id>")
        return

    subscription_id = int(command.args.strip())
    session_factory = get_session_factory()
    async with session_factory() as session:
        subscription = await approve_qr_subscription(session, subscription_id)
        if subscription is None:
            await message.answer("Заявка не найдена или уже обработана (ожидается pending + QR).")
            return
        user = await UserRepository(session).get_by_id(subscription.user_id)
        await session.commit()

    await message.answer(
        f"✅ Подписка #{subscription_id} активирована ({plan_label(subscription.plan)})."
    )

    if user is not None:
        expires = (
            subscription.expires_at.strftime("%d.%m.%Y")
            if subscription.expires_at
            else "—"
        )
        try:
            await bot.send_message(
                user.tg_id,
                f"✅ Ваша оплата по QR подтверждена!\n\n"
                f"Тариф: <b>{plan_label(subscription.plan)}</b>\n"
                f"Активна до: <b>{expires}</b>",
            )
        except Exception:
            await message.answer("Подписка активирована, но не удалось уведомить пользователя в Telegram.")


@router.message(Command("reject"))
async def reject_subscription(message: Message, command: CommandObject, bot: Bot) -> None:
    if message.from_user is None or not _is_admin(message.from_user.id):
        await message.answer("Команда доступна только администраторам.")
        return
    if not command.args or not command.args.strip().isdigit():
        await message.answer("Использование: /reject <subscription_id>")
        return

    subscription_id = int(command.args.strip())
    session_factory = get_session_factory()
    async with session_factory() as session:
        subscription = await reject_qr_subscription(session, subscription_id)
        if subscription is None:
            await message.answer("Заявка не найдена или уже не в статусе pending.")
            return
        user = await UserRepository(session).get_by_id(subscription.user_id)
        await session.commit()

    await message.answer(f"❌ Заявка #{subscription_id} отклонена.")
    if user is not None:
        try:
            await bot.send_message(
                user.tg_id,
                "Оплата по QR не подтверждена. Если вы уже платили — напишите в поддержку.",
            )
        except Exception:
            pass


@router.message(Command("stats"))
async def admin_stats(message: Message) -> None:
    if message.from_user is None or not _is_admin(message.from_user.id):
        await message.answer("Команда доступна только администраторам.")
        return
    session_factory = get_session_factory()
    async with session_factory() as session:
        text = await build_stats_message(session)
    await message.answer(text)


@router.message(Command("pending"))
async def admin_pending(message: Message) -> None:
    if message.from_user is None or not _is_admin(message.from_user.id):
        await message.answer("Команда доступна только администраторам.")
        return
    session_factory = get_session_factory()
    async with session_factory() as session:
        pending = await SubscriptionRepository(session).list_pending()
        lines = ["<b>Pending-платежи</b>", ""]
        if not pending:
            lines.append("Нет заявок в ожидании.")
        else:
            for sub in pending:
                user = await UserRepository(session).get_by_id(sub.user_id)
                tg = user.tg_id if user else "?"
                method = sub.payment_method.value if sub.payment_method else "—"
                lines.append(
                    f"#{sub.id} user={tg} plan={sub.plan.value} method={method}"
                )
    await message.answer("\n".join(lines))


@router.message(Command("broadcast"))
async def admin_broadcast(message: Message, command: CommandObject, bot: Bot) -> None:
    if message.from_user is None or not _is_admin(message.from_user.id):
        await message.answer("Команда доступна только администраторам.")
        return
    if not command.args or not command.args.strip():
        await message.answer(
            "Использование:\n"
            "/broadcast preview Текст — показать число получателей\n"
            "/broadcast send Текст — отправить всем"
        )
        return

    raw = command.args.strip()
    if raw.startswith("preview "):
        mode = "preview"
        text = raw.removeprefix("preview ").strip()
    elif raw.startswith("send "):
        mode = "send"
        text = raw.removeprefix("send ").strip()
    else:
        await message.answer("Укажите режим: preview или send (см. /broadcast).")
        return

    if not text:
        await message.answer("Пустой текст рассылки.")
        return

    session_factory = get_session_factory()
    async with session_factory() as session:
        from sqlalchemy import select

        from app.db.models import User

        result = await session.execute(select(User))
        users = list(result.scalars().all())

    if mode == "preview":
        await message.answer(
            f"<b>Предпросмотр рассылки</b>\n\n"
            f"Получателей: <b>{len(users)}</b>\n\n"
            f"{text}\n\n"
            "Для отправки: /broadcast send …"
        )
        return

    sent = 0
    failed = 0
    for user in users:
        try:
            await bot.send_message(user.tg_id, text)
            sent += 1
        except Exception:
            failed += 1
        await asyncio.sleep(0.05)

    await message.answer(f"Рассылка завершена. Доставлено: {sent}, ошибок: {failed}.")
