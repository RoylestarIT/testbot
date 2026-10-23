from aiogram import Bot, Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from app.core.config import get_settings
from app.db.repositories.subscription import SubscriptionRepository
from app.db.repositories.user import UserRepository
from app.db.session import get_session_factory
from app.services.subscription import approve_qr_subscription, plan_label

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
