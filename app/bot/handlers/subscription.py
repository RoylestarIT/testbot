from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message, PreCheckoutQuery

from app.bot.keyboards.menu import main_menu_keyboard
from app.bot.keyboards.subscription import (
    crypto_pay_keyboard,
    qr_paid_keyboard,
    qr_plan_keyboard,
    subscription_menu_keyboard,
)
from app.core.config import get_settings
from app.bot.utils.callbacks import answer_and_edit
from app.db.models import SubscriptionPlan, User as DbUser
from app.db.repositories.user import UserRepository
from app.db.session import get_session_factory
from app.services.generation_limit import remaining_generations_today
from app.services.payment.crypto_pay import (
    CryptoPayError,
    create_subscription_invoice,
    crypto_amount_for_plan,
    crypto_pay_enabled,
)
from app.services.payment.manual_qr import qr_instructions
from app.services.payment.payment_options import card_payments_enabled, stars_payments_enabled
from app.services.payment.telegram_stars import (
    invoice_currency,
    invoice_description,
    invoice_payload,
    invoice_prices,
    invoice_provider_token,
    invoice_title,
    parse_invoice_payload,
    payment_method_for_invoice,
    payment_mode_label,
)
from app.services.plans import LITE_VS_PRO_SHORT, PLANS_COMPARISON_TEXT, describe_access_tier
from app.services.subscription import (
    activate_from_telegram_invoice,
    create_crypto_pending,
    create_qr_pending,
    format_subscription_summary,
    get_effective_subscription,
)
from app.tasks.crypto_pay_poller import process_crypto_pending_once

router = Router(name="subscription")

def _subscription_menu_text() -> str:
    from app.bot.ui import brand_title, footer_hint, kv, muted, section

    settings = get_settings()
    methods: list[str] = []
    if stars_payments_enabled(settings):
        methods.append("Telegram Stars")
    elif card_payments_enabled(settings):
        methods.append(payment_mode_label(settings))
    if crypto_pay_enabled(settings):
        methods.append("Crypto Bot (USDT/TON…)")
    methods.append("перевод РФ/РБ")
    pay_line = ", ".join(methods)
    return (
        brand_title("Подписка", tagline="Free · Lite · PRO", icon="💎")
        + section("Оплата", icon="💳")
        + f"\n  {kv('Способы', pay_line)}"
        + f"\n  {muted(LITE_VS_PRO_SHORT)}"
        + section("Перевод", icon="🏦")
        + "\n"
        + muted("РФ или РБ — заявка, подтверждение администратором.")
        + footer_hint("🪙 Crypto Bot — автоматически после оплаты счёта.")
    )


async def _subscription_status_text(db_user: DbUser) -> str:
    session_factory = get_session_factory()
    async with session_factory() as session:
        user = await UserRepository(session).get_by_id(db_user.id)
        subscription = await get_effective_subscription(session, db_user.id)
        remaining = await remaining_generations_today(session, db_user.id)
        tier_line = await describe_access_tier(session, user, subscription) if user else None
    return format_subscription_summary(
        db_user,
        subscription,
        generations_remaining=remaining,
        access_tier_line=tier_line,
    )


async def _notify_admins_qr(bot: Bot, *, subscription_id: int, db_user: DbUser, plan: SubscriptionPlan) -> None:
    settings = get_settings()
    if not settings.admin_ids:
        return
    plan_name = "PRO" if plan == SubscriptionPlan.PRO else "Lite"
    text = (
        "<b>Заявка на оплату QR</b>\n\n"
        f"Subscription ID: <code>{subscription_id}</code>\n"
        f"User DB id: <code>{db_user.id}</code>\n"
        f"Telegram tg_id: <code>{db_user.tg_id}</code>\n"
        f"Username: @{db_user.username or '—'}\n"
        f"План: <b>{plan_name}</b>\n\n"
        f"Активировать: /approve {subscription_id}"
    )
    for admin_id in settings.admin_ids:
        try:
            await bot.send_message(admin_id, text)
        except Exception:
            continue


@router.message(Command("my_subscription"))
async def cmd_my_subscription(message: Message, db_user: DbUser) -> None:
    text = await _subscription_status_text(db_user)
    await message.answer(text, reply_markup=subscription_menu_keyboard())


@router.callback_query(F.data == "menu:subscription")
async def menu_subscription(callback: CallbackQuery, db_user: DbUser) -> None:
    text = await _subscription_status_text(db_user)
    await answer_and_edit(
        callback,
        f"{_subscription_menu_text()}\n\n{text}",
        reply_markup=subscription_menu_keyboard(),
    )


@router.callback_query(F.data == "sub:status")
async def subscription_status(callback: CallbackQuery, db_user: DbUser) -> None:
    text = await _subscription_status_text(db_user)
    await answer_and_edit(callback, text, reply_markup=subscription_menu_keyboard())


@router.callback_query(F.data == "sub:compare")
async def subscription_compare(callback: CallbackQuery) -> None:
    await answer_and_edit(callback, PLANS_COMPARISON_TEXT, reply_markup=subscription_menu_keyboard())


@router.callback_query(F.data.in_({"sub:stars:lite", "sub:stars:pro"}))
async def send_stars_invoice(callback: CallbackQuery, bot: Bot, db_user: DbUser) -> None:
    plan = SubscriptionPlan.PRO if callback.data.endswith(":pro") else SubscriptionPlan.LITE
    settings = get_settings()
    if not stars_payments_enabled(settings) and not card_payments_enabled(settings):
        await callback.answer(
            "Оплата картой/Stars не настроена. Используйте 🪙 Crypto Bot или перевод.",
            show_alert=True,
        )
        return
    await callback.answer()
    if not callback.message:
        return
    await bot.send_invoice(
        chat_id=callback.message.chat.id,
        title=invoice_title(plan),
        description=invoice_description(plan, settings),
        payload=invoice_payload(plan, db_user.id),
        currency=invoice_currency(settings),
        prices=invoice_prices(settings, plan),
        provider_token=invoice_provider_token(settings),
    )


@router.pre_checkout_query()
async def pre_checkout_handler(pre_checkout: PreCheckoutQuery, db_user: DbUser) -> None:
    parsed = parse_invoice_payload(pre_checkout.invoice_payload)
    if parsed is None:
        await pre_checkout.answer(ok=False, error_message="Некорректный платёж")
        return
    plan, user_id = parsed
    if user_id != db_user.id:
        await pre_checkout.answer(ok=False, error_message="Платёж привязан к другому пользователю")
        return
    if plan not in (SubscriptionPlan.LITE, SubscriptionPlan.PRO):
        await pre_checkout.answer(ok=False, error_message="Неизвестный тариф")
        return
    await pre_checkout.answer(ok=True)


@router.message(F.successful_payment)
async def successful_payment_handler(message: Message, db_user: DbUser) -> None:
    payment = message.successful_payment
    if payment is None:
        return
    parsed = parse_invoice_payload(payment.invoice_payload)
    if parsed is None:
        await message.answer("Платёж получен, но не удалось определить тариф. Напишите в поддержку.")
        return
    plan, user_id = parsed
    if user_id != db_user.id:
        await message.answer("Ошибка привязки платежа.")
        return

    charge_id = payment.telegram_payment_charge_id
    settings = get_settings()
    session_factory = get_session_factory()
    async with session_factory() as session:
        await activate_from_telegram_invoice(
            session,
            user_id=db_user.id,
            plan=plan,
            telegram_payment_charge_id=charge_id,
            payment_method=payment_method_for_invoice(settings),
        )
        await session.commit()
        subscription = await get_effective_subscription(session, db_user.id)

    plan_name = "PRO" if plan == SubscriptionPlan.PRO else "Lite"
    expires = subscription.expires_at.strftime("%d.%m.%Y") if subscription and subscription.expires_at else "—"
    await message.answer(
        f"✅ Оплата принята ({payment_mode_label(settings)})!\n\n"
        f"Тариф: <b>{plan_name}</b>\n"
        f"Активна до: <b>{expires}</b>\n\n"
        "Спасибо за подписку!",
        reply_markup=main_menu_keyboard(),
    )


@router.callback_query(F.data.in_({"sub:crypto:lite", "sub:crypto:pro"}))
async def crypto_create_invoice(callback: CallbackQuery, bot: Bot, db_user: DbUser) -> None:
    settings = get_settings()
    if not crypto_pay_enabled(settings):
        await callback.answer("Crypto Bot не настроен", show_alert=True)
        return
    plan = SubscriptionPlan.PRO if callback.data.endswith(":pro") else SubscriptionPlan.LITE
    session_factory = get_session_factory()
    async with session_factory() as session:
        subscription = await create_crypto_pending(session, user_id=db_user.id, plan=plan)
        await session.flush()
        try:
            invoice = await create_subscription_invoice(
                settings,
                subscription_id=subscription.id,
                user_id=db_user.id,
                plan=plan,
            )
        except CryptoPayError as exc:
            await callback.answer("Не удалось создать счёт", show_alert=True)
            if callback.message:
                await callback.message.answer(f"Crypto Bot: {exc}")
            return
        subscription.external_payment_id = str(invoice.get("invoice_id", ""))
        await session.commit()

    pay_url = invoice.get("bot_invoice_url") or invoice.get("pay_url") or invoice.get("mini_app_invoice_url")
    if not pay_url:
        await callback.answer("Нет ссылки на оплату", show_alert=True)
        return
    plan_name = "PRO" if plan == SubscriptionPlan.PRO else "Lite"
    await callback.answer()
    if callback.message:
        await callback.message.edit_text(
            f"🪙 <b>Оплата {plan_name}</b>\n\n"
            f"Сумма: <b>${crypto_amount_for_plan(settings, plan)}</b> (можно оплатить USDT, TON и др.)\n"
            "Нажмите кнопку ниже — откроется @CryptoBot.\n"
            "После оплаты доступ включится автоматически (до 2 минут).",
            reply_markup=crypto_pay_keyboard(str(pay_url)),
        )


@router.callback_query(F.data == "sub:crypto:check")
async def crypto_check_payment(callback: CallbackQuery, bot: Bot, db_user: DbUser) -> None:
    await callback.answer("Проверяю…")
    await process_crypto_pending_once(bot)
    text = await _subscription_status_text(db_user)
    if callback.message:
        await callback.message.answer(text, reply_markup=subscription_menu_keyboard())


@router.callback_query(F.data == "sub:qr:menu")
async def qr_plan_menu(callback: CallbackQuery) -> None:
    await callback.answer()
    if callback.message:
        await callback.message.edit_text(
            "Выберите тариф для оплаты переводом (РФ / РБ):",
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
async def qr_mark_paid(callback: CallbackQuery, bot: Bot, db_user: DbUser) -> None:
    plan_key = callback.data.split(":")[-1]
    plan = SubscriptionPlan.PRO if plan_key == "pro" else SubscriptionPlan.LITE
    session_factory = get_session_factory()
    async with session_factory() as session:
        subscription = await create_qr_pending(session, user_id=db_user.id, plan=plan)
        await session.commit()
        sub_id = subscription.id

    await _notify_admins_qr(bot, subscription_id=sub_id, db_user=db_user, plan=plan)
    await callback.answer("Заявка отправлена администратору")
    if callback.message:
        await callback.message.edit_text(
            "✅ Заявка на оплату QR создана.\n\n"
            f"Номер заявки: <code>{sub_id}</code>\n"
            "После проверки перевода администратор активирует подписку.",
            reply_markup=subscription_menu_keyboard(),
        )
