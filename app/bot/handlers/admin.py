from aiogram import Bot, Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from app.core.config import get_settings
from app.db.repositories.subscription import SubscriptionRepository
from app.db.repositories.user import UserRepository
from app.db.session import get_session_factory
from app.services.admin_stats import build_stats_message
from app.services.subscription import approve_qr_subscription, plan_label, reject_qr_subscription

router = Router(name="admin")


def _is_admin(telegram_id: int) -> bool:
    return telegram_id in get_settings().admin_ids


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

    import asyncio

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
