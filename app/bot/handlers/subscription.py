from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message, PreCheckoutQuery

from app.bot.keyboards.menu import main_menu_keyboard
from app.bot.keyboards.subscription import (
    qr_paid_keyboard,
    qr_plan_keyboard,
    subscription_menu_keyboard,
)
from app.core.config import get_settings
from app.db.models import SubscriptionPlan, User
from app.db.session import get_session_factory
from app.services.generation_limit import remaining_generations_today
from app.services.payment.manual_qr import qr_instructions
from app.services.payment.telegram_stars import (
    STARS_CURRENCY,
    invoice_description,
    invoice_payload,
    invoice_prices,
    invoice_title,
    parse_invoice_payload,
)
from app.services.subscription import (
    activate_from_stars,
    create_qr_pending,
    format_subscription_summary,
    get_effective_subscription,
)

router = Router(name="subscription")

SUBSCRIPTION_MENU_TEXT = (
    "<b>Подписка ReviewPilot</b>\n\n"
    "• <b>Lite</b> — ~$10/мес (Telegram Stars или QR для РБ)\n"
    "• <b>PRO</b> — ~$30/мес, без лимита генераций и PRO-функции\n\n"
    "Бесплатный Lite: до 5 генераций в день."
)


async def _subscription_status_text(user: User) -> str:
    session_factory = get_session_factory()
    async with session_factory() as session:
        subscription = await get_effective_subscription(session, user.id)
        remaining = await remaining_generations_today(session, user.id)
    return format_subscription_summary(user, subscription, generations_remaining=remaining)


async def _notify_admins_qr(bot: Bot, *, subscription_id: int, user: User, plan: SubscriptionPlan) -> None:
    settings = get_settings()
    if not settings.admin_ids:
        return
    plan_name = "PRO" if plan == SubscriptionPlan.PRO else "Lite"
    text = (
        "<b>Заявка на оплату QR</b>\n\n"
        f"Subscription ID: <code>{subscription_id}</code>\n"
        f"User DB id: <code>{user.id}</code>\n"
        f"Telegram tg_id: <code>{user.tg_id}</code>\n"
        f"Username: @{user.username or '—'}\n"
        f"План: <b>{plan_name}</b>\n\n"
        f"Активировать: /approve {subscription_id}"
    )
    for admin_id in settings.admin_ids:
        try:
            await bot.send_message(admin_id, text)
        except Exception:
            continue


@router.message(Command("my_subscription"))
async def cmd_my_subscription(message: Message, user: User) -> None:
    text = await _subscription_status_text(user)
    await message.answer(text, reply_markup=subscription_menu_keyboard())


@router.callback_query(F.data == "menu:subscription")
async def menu_subscription(callback: CallbackQuery, user: User) -> None:
    await callback.answer()
    if callback.message:
        text = await _subscription_status_text(user)
        await callback.message.edit_text(
            f"{SUBSCRIPTION_MENU_TEXT}\n\n{text}",
            reply_markup=subscription_menu_keyboard(),
        )


@router.callback_query(F.data == "sub:status")
async def subscription_status(callback: CallbackQuery, user: User) -> None:
    await callback.answer()
    if callback.message:
        text = await _subscription_status_text(user)
        await callback.message.edit_text(text, reply_markup=subscription_menu_keyboard())


@router.callback_query(F.data.in_({"sub:stars:lite", "sub:stars:pro"}))
async def send_stars_invoice(callback: CallbackQuery, bot: Bot, user: User) -> None:
    plan = SubscriptionPlan.PRO if callback.data.endswith(":pro") else SubscriptionPlan.LITE
    settings = get_settings()
    await callback.answer()
    if not callback.message:
        return
    await bot.send_invoice(
        chat_id=callback.message.chat.id,
        title=invoice_title(plan),
        description=invoice_description(plan, settings),
        payload=invoice_payload(plan, user.id),
        currency=STARS_CURRENCY,
        prices=invoice_prices(settings, plan),
        provider_token="",
    )


@router.pre_checkout_query()
async def pre_checkout_handler(pre_checkout: PreCheckoutQuery, user: User) -> None:
    parsed = parse_invoice_payload(pre_checkout.invoice_payload)
    if parsed is None:
        await pre_checkout.answer(ok=False, error_message="Некорректный платёж")
        return
    plan, user_id = parsed
    if user_id != user.id:
        await pre_checkout.answer(ok=False, error_message="Платёж привязан к другому пользователю")
        return
    if plan not in (SubscriptionPlan.LITE, SubscriptionPlan.PRO):
        await pre_checkout.answer(ok=False, error_message="Неизвестный тариф")
        return
    await pre_checkout.answer(ok=True)


@router.message(F.successful_payment)
async def successful_payment_handler(message: Message, user: User) -> None:
    payment = message.successful_payment
    if payment is None:
        return
    parsed = parse_invoice_payload(payment.invoice_payload)
    if parsed is None:
        await message.answer("Платёж получен, но не удалось определить тариф. Напишите в поддержку.")
        return
    plan, user_id = parsed
    if user_id != user.id:
        await message.answer("Ошибка привязки платежа.")
        return

    charge_id = payment.telegram_payment_charge_id
    session_factory = get_session_factory()
    async with session_factory() as session:
        await activate_from_stars(
            session,
            user_id=user.id,
            plan=plan,
            telegram_payment_charge_id=charge_id,
        )
        await session.commit()
        subscription = await get_effective_subscription(session, user.id)

    plan_name = "PRO" if plan == SubscriptionPlan.PRO else "Lite"
    expires = subscription.expires_at.strftime("%d.%m.%Y") if subscription and subscription.expires_at else "—"
    await message.answer(
        f"✅ Оплата Stars принята!\n\n"
        f"Тариф: <b>{plan_name}</b>\n"
        f"Активна до: <b>{expires}</b>\n\n"
        "Спасибо за подписку!",
        reply_markup=main_menu_keyboard(),
    )


@router.callback_query(F.data == "sub:qr:menu")
async def qr_plan_menu(callback: CallbackQuery) -> None:
    await callback.answer()
    if callback.message:
        await callback.message.edit_text(
            "Выберите тариф для оплаты по QR (Беларусь):",
            reply_markup=qr_plan_keyboard(),
        )


@router.callback_query(F.data.in_({"sub:qr:lite", "sub:qr:pro"}))
async def qr_show_instructions(callback: CallbackQuery) -> None:
    plan_key = callback.data.split(":")[-1]
    plan = SubscriptionPlan.PRO if plan_key == "pro" else SubscriptionPlan.LITE
    settings = get_settings()
    await callback.answer()
    if callback.message:
        await callback.message.edit_text(
            qr_instructions(settings, plan),
            reply_markup=qr_paid_keyboard(plan_key),
        )


@router.callback_query(F.data.startswith("sub:qr:paid:"))
async def qr_mark_paid(callback: CallbackQuery, bot: Bot, user: User) -> None:
    plan_key = callback.data.split(":")[-1]
    plan = SubscriptionPlan.PRO if plan_key == "pro" else SubscriptionPlan.LITE
    session_factory = get_session_factory()
    async with session_factory() as session:
        subscription = await create_qr_pending(session, user_id=user.id, plan=plan)
        await session.commit()
        sub_id = subscription.id

    await _notify_admins_qr(bot, subscription_id=sub_id, user=user, plan=plan)
    await callback.answer("Заявка отправлена администратору")
    if callback.message:
        await callback.message.edit_text(
            "✅ Заявка на оплату QR создана.\n\n"
            f"Номер заявки: <code>{sub_id}</code>\n"
            "После проверки перевода администратор активирует подписку.",
            reply_markup=subscription_menu_keyboard(),
        )
