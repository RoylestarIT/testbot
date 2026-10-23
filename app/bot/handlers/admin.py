from __future__ import annotations

import asyncio

from aiogram import Bot, F, Router
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.bot.keyboards.admin import (
    admin_back_keyboard,
    admin_menu_keyboard,
    admin_user_card_keyboard,
    broadcast_cancel_keyboard,
    broadcast_preview_keyboard,
    grant_cancel_keyboard,
    grant_plan_keyboard,
    pending_detail_keyboard,
)
from app.services.admin_audit import notify_admins
from app.services.pro_access import admin_extend_trial
from app.services.subscription import expire_active_subscriptions
from app.bot.keyboards.menu import main_menu_keyboard
from app.bot.states.admin import AdminStates
from app.core.config import get_settings
from app.db.models import SubscriptionPlan
from app.db.repositories.subscription import SubscriptionRepository
from app.db.repositories.promo_code import PromoCodeRepository
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
    "✨ <b>ReviewPilot</b>\n🛠 <b>Админ-панель</b>\n\n"
    "<i>Заявки, пользователи, рассылка и промокоды.</i>"
)


def _is_admin(telegram_id: int) -> bool:
    return telegram_id in get_settings().admin_ids


async def _count_users() -> int:
    from sqlalchemy import func, select

    from app.db.models import User

    session_factory = get_session_factory()
    async with session_factory() as session:
        result = await session.scalar(select(func.count()).select_from(User))
        return int(result or 0)


async def _list_all_user_tg_ids() -> list[int]:
    from sqlalchemy import select

    from app.db.models import User

    session_factory = get_session_factory()
    async with session_factory() as session:
        result = await session.execute(select(User.tg_id))
        return [int(row[0]) for row in result.all()]


async def _render_pending_message(index: int) -> tuple[str, int | None, int]:
    session_factory = get_session_factory()
    async with session_factory() as session:
        pending = await SubscriptionRepository(session).list_pending()
        total = len(pending)
        if total == 0:
            return "⏳ <b>Pending</b>\n\nЗаявок нет.", None, 0
        index = max(0, min(index, total - 1))
        sub = pending[index]
        user = await UserRepository(session).get_by_id(sub.user_id)
    tg = user.tg_id if user else "?"
    uname = f"@{user.username}" if user and user.username else "—"
    text = (
        f"⏳ <b>Заявка {index + 1} из {total}</b>\n\n"
        f"Subscription ID: <code>{sub.id}</code>\n"
        f"Telegram ID: <code>{tg}</code>\n"
        f"Username: {uname}\n"
        f"Тариф: <b>{plan_label(sub.plan)}</b>\n"
        f"Оплата: {sub.payment_method.value if sub.payment_method else '—'}"
    )
    return text, sub.id, total


async def _execute_grant(bot: Bot, tg_id: int, plan: SubscriptionPlan) -> tuple[str, bool]:
    session_factory = get_session_factory()
    async with session_factory() as session:
        subscription, err = await grant_subscription_by_tg_id(session, tg_id=tg_id, plan=plan)
        if subscription is None:
            return err or "Не удалось выдать подписку.", False
        await session.commit()

    msg = (
        f"✅ Выдан <b>{plan_label(plan)}</b> пользователю <code>{tg_id}</code>\n"
        f"Subscription #{subscription.id}"
    )
    notify_ok = True
    try:
        expires = subscription.expires_at.strftime("%d.%m.%Y") if subscription.expires_at else "—"
        await bot.send_message(
            tg_id,
            f"🎁 Вам активирован тариф <b>{plan_label(plan)}</b>.\nДействует до: <b>{expires}</b>",
        )
    except Exception:
        notify_ok = False
    if not notify_ok:
        msg += "\n\n⚠️ Не удалось уведомить пользователя в Telegram."
    return msg, True


async def _execute_broadcast(bot: Bot, text: str) -> str:
    tg_ids = await _list_all_user_tg_ids()
    sent = 0
    failed = 0
    for tg_id in tg_ids:
        try:
            await bot.send_message(tg_id, text)
            sent += 1
        except Exception:
            failed += 1
        await asyncio.sleep(0.05)
    return f"📢 Рассылка завершена.\nДоставлено: <b>{sent}</b>, ошибок: <b>{failed}</b>."


@router.message(Command("admin"))
async def cmd_admin(message: Message) -> None:
    if message.from_user is None or not _is_admin(message.from_user.id):
        await message.answer("Команда доступна только администраторам.")
        return
    await message.answer(ADMIN_PANEL_TEXT, reply_markup=admin_menu_keyboard())


@router.callback_query(F.data == "menu:admin")
async def menu_admin(callback: CallbackQuery, state: FSMContext) -> None:
    if callback.from_user is None or not _is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return
    await state.clear()
    await callback.answer()
    if callback.message:
        await callback.message.edit_text(ADMIN_PANEL_TEXT, reply_markup=admin_menu_keyboard())


@router.callback_query(F.data == "admin:noop")
async def admin_noop(callback: CallbackQuery) -> None:
    await callback.answer()


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
        await callback.message.edit_text(text, reply_markup=admin_back_keyboard())


@router.callback_query(F.data.startswith("admin:pending:"))
async def admin_pending_callback(callback: CallbackQuery) -> None:
    if callback.from_user is None or not _is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return
    index = int(callback.data.split(":")[-1])
    text, sub_id, total = await _render_pending_message(index)
    await callback.answer()
    if callback.message:
        if sub_id is None:
            await callback.message.edit_text(text, reply_markup=admin_menu_keyboard())
        else:
            await callback.message.edit_text(
                text,
                reply_markup=pending_detail_keyboard(sub_id, index, total),
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
    await callback.answer("Подтверждено")
    if user is not None:
        expires = subscription.expires_at.strftime("%d.%m.%Y") if subscription.expires_at else "—"
        try:
            await bot.send_message(
                user.tg_id,
                f"✅ Оплата подтверждена!\n\nТариф: <b>{plan_label(subscription.plan)}</b>\nДо: <b>{expires}</b>",
            )
        except Exception:
            pass
    text, sub_id, total = await _render_pending_message(0)
    if callback.message:
        if sub_id is None:
            await callback.message.edit_text(
                f"✅ Заявка #{subscription_id} активирована.\n\n{text}",
                reply_markup=admin_menu_keyboard(),
            )
        else:
            await callback.message.edit_text(
                f"✅ Заявка #{subscription_id} активирована.\n\n{text}",
                reply_markup=pending_detail_keyboard(sub_id, 0, total),
            )


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
    if user is not None:
        try:
            await bot.send_message(user.tg_id, "Заявка на оплату не подтверждена.")
        except Exception:
            pass
    text, sub_id, total = await _render_pending_message(0)
    if callback.message:
        if sub_id is None:
            await callback.message.edit_text(
                f"❌ Заявка #{subscription_id} отклонена.\n\n{text}",
                reply_markup=admin_menu_keyboard(),
            )
        else:
            await callback.message.edit_text(
                f"❌ Заявка #{subscription_id} отклонена.\n\n{text}",
                reply_markup=pending_detail_keyboard(sub_id, 0, total),
            )


@router.callback_query(F.data == "admin:grant")
async def admin_grant_start(callback: CallbackQuery, state: FSMContext) -> None:
    if callback.from_user is None or not _is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return
    await state.set_state(AdminStates.waiting_grant_tg_id)
    await callback.answer()
    if callback.message:
        await callback.message.edit_text(
            "🎁 <b>Выдача подписки</b>\n\n"
            "Пришлите <b>Telegram ID</b> пользователя (число).\n"
            "Пользователь должен хотя бы раз нажать /start в боте.",
            reply_markup=grant_cancel_keyboard(),
        )


@router.callback_query(F.data == "admin:grant:cancel")
async def admin_grant_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.answer("Отменено")
    if callback.message:
        await callback.message.edit_text(ADMIN_PANEL_TEXT, reply_markup=admin_menu_keyboard())


@router.message(AdminStates.waiting_grant_tg_id, F.text)
async def admin_grant_tg_id(message: Message, state: FSMContext) -> None:
    if message.from_user is None or not _is_admin(message.from_user.id):
        return
    raw = (message.text or "").strip()
    if not raw.isdigit():
        await message.answer("Нужен числовой Telegram ID.", reply_markup=grant_cancel_keyboard())
        return
    await state.update_data(grant_tg_id=int(raw))
    await state.set_state(AdminStates.waiting_grant_tg_id)  # stay until plan picked
    await message.answer(
        f"Пользователь: <code>{raw}</code>\n\nВыберите тариф:",
        reply_markup=grant_plan_keyboard(),
    )


@router.callback_query(F.data.startswith("admin:grant:plan:"))
async def admin_grant_plan(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    if callback.from_user is None or not _is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return
    plan_raw = callback.data.split(":")[-1]
    plan = SubscriptionPlan.PRO if plan_raw == "pro" else SubscriptionPlan.LITE
    data = await state.get_data()
    tg_id = data.get("grant_tg_id")
    if tg_id is None:
        await state.clear()
        await callback.answer("Начните заново", show_alert=True)
        return
    await callback.answer("Выдаю…")
    msg, _ = await _execute_grant(bot, int(tg_id), plan)
    await state.clear()
    if callback.message:
        await callback.message.edit_text(msg, reply_markup=admin_menu_keyboard())


@router.callback_query(F.data == "admin:broadcast")
async def admin_broadcast_start(callback: CallbackQuery, state: FSMContext) -> None:
    if callback.from_user is None or not _is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return
    await state.set_state(AdminStates.waiting_broadcast_text)
    await callback.answer()
    if callback.message:
        await callback.message.edit_text(
            "📢 <b>Рассылка</b>\n\nПришлите текст одним сообщением (HTML как в боте).",
            reply_markup=broadcast_cancel_keyboard(),
        )


@router.callback_query(F.data == "admin:broadcast:cancel")
async def admin_broadcast_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.answer("Отменено")
    if callback.message:
        await callback.message.edit_text(ADMIN_PANEL_TEXT, reply_markup=admin_menu_keyboard())


@router.message(AdminStates.waiting_broadcast_text, F.text)
async def admin_broadcast_preview(message: Message, state: FSMContext) -> None:
    if message.from_user is None or not _is_admin(message.from_user.id):
        return
    text = (message.text or "").strip()
    if len(text) < 2:
        await message.answer("Текст слишком короткий.")
        return
    await state.update_data(broadcast_text=text)
    count = await _count_users()
    await message.answer(
        f"📢 <b>Предпросмотр</b>\n\n"
        f"Получателей: <b>{count}</b>\n\n"
        f"{text}",
        reply_markup=broadcast_preview_keyboard(),
    )


@router.callback_query(F.data == "admin:broadcast:send")
async def admin_broadcast_send(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    if callback.from_user is None or not _is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return
    data = await state.get_data()
    text = data.get("broadcast_text")
    if not text:
        await callback.answer("Текст утерян", show_alert=True)
        await state.clear()
        return
    await callback.answer("Отправляю…")
    result = await _execute_broadcast(bot, str(text))
    await state.clear()
    if callback.message:
        await callback.message.edit_text(result, reply_markup=admin_menu_keyboard())


async def _build_user_card(session, user_id: int) -> str | None:
    user = await UserRepository(session).get_by_id(user_id)
    if user is None:
        return None
    from app.services.dashboard import build_user_dashboard

    header = (
        f"👤 <b>Пользователь</b> db_id={user.id}\n"
        f"tg_id: <code>{user.tg_id}</code>\n"
        f"username: @{user.username or '—'}\n"
    )
    body = await build_user_dashboard(session, user)
    return header + "\n" + body


@router.callback_query(F.data == "admin:find_user")
async def admin_find_user_start(callback: CallbackQuery, state: FSMContext) -> None:
    if callback.from_user is None or not _is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return
    await state.set_state(AdminStates.waiting_user_query)
    await callback.answer()
    if callback.message:
        await callback.message.edit_text(
            "👤 Пришлите <b>Telegram ID</b> или <b>@username</b>:",
            reply_markup=admin_back_keyboard(),
        )


@router.message(AdminStates.waiting_user_query, F.text)
async def admin_find_user_query(message: Message, state: FSMContext, bot: Bot) -> None:
    if message.from_user is None or not _is_admin(message.from_user.id):
        return
    raw = (message.text or "").strip()
    session_factory = get_session_factory()
    async with session_factory() as session:
        user = None
        if raw.isdigit():
            user = await UserRepository(session).get_by_tg_id(int(raw))
        elif raw.startswith("@"):
            user = await UserRepository(session).get_by_username(raw)
        if user is None:
            await message.answer("Не найден.", reply_markup=admin_menu_keyboard())
            await state.clear()
            return
        text = await _build_user_card(session, user.id)
    await state.clear()
    if text:
        await message.answer(text, reply_markup=admin_user_card_keyboard(user.id))
        await notify_admins(bot, f"Admin opened user card db_id={user.id}")


@router.callback_query(F.data.startswith("admin:user:grant:"))
async def admin_user_grant(callback: CallbackQuery, bot: Bot) -> None:
    if callback.from_user is None or not _is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return
    parts = callback.data.split(":")
    plan = SubscriptionPlan.PRO if parts[3] == "pro" else SubscriptionPlan.LITE
    user_id = int(parts[4])
    session_factory = get_session_factory()
    async with session_factory() as session:
        user = await UserRepository(session).get_by_id(user_id)
        if user is None:
            await callback.answer("Не найден", show_alert=True)
            return
        msg, ok = await _execute_grant(bot, user.tg_id, plan)
        await session.commit()
    await callback.answer("OK" if ok else "Ошибка", show_alert=True)
    if callback.message:
        await callback.message.answer(msg, reply_markup=admin_user_card_keyboard(user_id))
    await notify_admins(bot, f"Grant {plan.value} to user db_id={user_id}")


@router.callback_query(F.data.startswith("admin:user:trial:"))
async def admin_user_trial(callback: CallbackQuery, bot: Bot) -> None:
    if callback.from_user is None or not _is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return
    parts = callback.data.split(":")
    days = int(parts[3])
    user_id = int(parts[4])
    session_factory = get_session_factory()
    async with session_factory() as session:
        user = await admin_extend_trial(session, user_id, days)
        await session.commit()
    if user is None:
        await callback.answer("Не найден", show_alert=True)
        return
    await callback.answer("Trial продлён")
    await notify_admins(bot, f"Trial +{days}d user db_id={user_id}")
    if callback.message:
        await callback.message.answer(
            f"Trial PRO до {user.trial_pro_until.strftime('%d.%m.%Y') if user.trial_pro_until else '—'}",
            reply_markup=admin_user_card_keyboard(user_id),
        )


@router.callback_query(F.data.startswith("admin:user:revoke:"))
async def admin_user_revoke(callback: CallbackQuery, bot: Bot) -> None:
    if callback.from_user is None or not _is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return
    user_id = int(callback.data.split(":")[-1])
    from datetime import UTC, datetime

    session_factory = get_session_factory()
    async with session_factory() as session:
        user = await UserRepository(session).get_by_id(user_id)
        if user is None:
            await callback.answer("Не найден", show_alert=True)
            return
        await expire_active_subscriptions(session, user_id)
        user.trial_pro_until = datetime.now(UTC)
        await session.commit()
    await callback.answer("PRO снят")
    await notify_admins(bot, f"Revoke PRO user db_id={user_id}")
    try:
        await bot.send_message(user.tg_id, "Подписка PRO/trial завершена администратором.")
    except Exception:
        pass


@router.callback_query(F.data == "admin:promo")
async def admin_promo_info(callback: CallbackQuery) -> None:
    if callback.from_user is None or not _is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return
    session_factory = get_session_factory()
    async with session_factory() as session:
        promos = await PromoCodeRepository(session).list_active()
    lines = ["🎟 <b>Промокоды</b>\n"]
    if not promos:
        lines.append("Активных кодов нет.")
    else:
        for p in promos[:10]:
            lines.append(
                f"• <code>{p.code}</code> +{p.trial_days}d trial · "
                f"{p.redemption_count}/{p.max_redemptions}"
            )
    lines.append("\nСоздать: <code>/promo_create КОД дней max_uses</code>")
    lines.append("Пользователь: <code>/promo КОД</code>")
    await callback.answer()
    if callback.message:
        await callback.message.edit_text("\n".join(lines), reply_markup=admin_back_keyboard())


@router.message(Command("promo_create"))
async def admin_promo_create(message: Message, command: CommandObject) -> None:
    if message.from_user is None or not _is_admin(message.from_user.id):
        return
    parts = (command.args or "").split()
    if len(parts) != 3 or not parts[1].isdigit() or not parts[2].isdigit():
        await message.answer("Формат: /promo_create SALE7 7 100")
        return
    session_factory = get_session_factory()
    async with session_factory() as session:
        promo = await PromoCodeRepository(session).create(
            code=parts[0],
            trial_days=int(parts[1]),
            max_redemptions=int(parts[2]),
        )
        await session.commit()
    await message.answer(
        f"✅ Промокод <code>{promo.code}</code> (+{promo.trial_days}d, max {promo.max_redemptions})",
        reply_markup=admin_menu_keyboard(),
    )


# --- Команды оставлены как запасной вариант ---


@router.message(Command("grant"))
async def grant_subscription_cmd(message: Message, command: CommandObject, bot: Bot) -> None:
    if message.from_user is None or not _is_admin(message.from_user.id):
        await message.answer("Команда доступна только администраторам.")
        return
    parts = (command.args or "").split()
    if len(parts) != 2 or not parts[0].isdigit():
        await message.answer("Или используйте кнопку «Выдать подписку» в /admin")
        return
    plan = SubscriptionPlan.PRO if parts[1].lower() == "pro" else SubscriptionPlan.LITE
    msg, _ = await _execute_grant(bot, int(parts[0]), plan)
    await message.answer(msg, reply_markup=admin_menu_keyboard())


@router.message(Command("approve"))
async def approve_subscription_cmd(message: Message, command: CommandObject, bot: Bot) -> None:
    if message.from_user is None or not _is_admin(message.from_user.id):
        return
    if not command.args or not command.args.strip().isdigit():
        await message.answer("Используйте Pending в /admin")
        return
    subscription_id = int(command.args.strip())
    session_factory = get_session_factory()
    async with session_factory() as session:
        subscription = await approve_qr_subscription(session, subscription_id)
        if subscription is None:
            await message.answer("Заявка не найдена.")
            return
        user = await UserRepository(session).get_by_id(subscription.user_id)
        await session.commit()
    await message.answer(f"✅ #{subscription_id} активирована.", reply_markup=admin_menu_keyboard())
    if user is not None and subscription.expires_at:
        try:
            await bot.send_message(
                user.tg_id,
                f"✅ Подписка активна до {subscription.expires_at.strftime('%d.%m.%Y')}",
            )
        except Exception:
            pass


@router.message(Command("stats"))
async def admin_stats_cmd(message: Message) -> None:
    if message.from_user is None or not _is_admin(message.from_user.id):
        return
    session_factory = get_session_factory()
    async with session_factory() as session:
        text = await build_stats_message(session)
    await message.answer(text, reply_markup=admin_menu_keyboard())


@router.message(Command("pending"))
async def admin_pending_cmd(message: Message) -> None:
    if message.from_user is None or not _is_admin(message.from_user.id):
        return
    text, sub_id, total = await _render_pending_message(0)
    if sub_id is None:
        await message.answer(text, reply_markup=admin_menu_keyboard())
    else:
        await message.answer(text, reply_markup=pending_detail_keyboard(sub_id, 0, total))
