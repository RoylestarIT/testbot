from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message, PreCheckoutQuery

from app.bot.keyboards.menu import main_menu_keyboard
from app.bot.keyboards.subscription import (
    card_payment_keyboard,
    crypto_pay_keyboard,
    crypto_plan_keyboard,
    legal_paid_keyboard,
    legal_plan_keyboard,
    payment_methods_keyboard,
    qr_paid_keyboard,
    qr_plan_keyboard,
    subscription_hub_keyboard,
    subscription_menu_keyboard,
    subscription_subscreen_keyboard,
)
from app.bot.subscription_ui import build_my_access_text, build_payment_hub, build_subscription_hub
from app.bot.ui import muted
from app.services.pro_access import has_paid_pro
from app.core.config import get_settings
from app.bot.keyboards.subscription_calc import calculator_detail_keyboard, calculator_volumes_keyboard
from app.services.payment.subscription_calculator import (
    build_calculator_detail,
    build_calculator_table,
)
from app.bot.utils.callbacks import answer_and_edit, safe_edit_message
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
from app.services.payment.fx_rates import SubscriptionPricing, get_subscription_pricing
from app.services.payment.manual_qr import legal_payment_instructions, qr_instructions
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
from app.services.plans import PLANS_COMPARISON_TEXT, describe_access_tier
from app.services.subscription import (
    activate_from_telegram_invoice,
    create_crypto_pending,
    create_qr_pending,
    get_effective_subscription,
)
from app.tasks.crypto_pay_poller import process_crypto_pending_once

router = Router(name="subscription")

async def _subscription_access_line(db_user: DbUser) -> str:
    session_factory = get_session_factory()
    async with session_factory() as session:
        user = await UserRepository(session).get_by_id(db_user.id)
        subscription = await get_effective_subscription(session, db_user.id)
        if user is None:
            return "—"
        return await describe_access_tier(session, user, subscription)


async def _subscription_hub_text(db_user: DbUser, pricing: SubscriptionPricing) -> str:
    access = await _subscription_access_line(db_user)
    trial_line: str | None = None
    session_factory = get_session_factory()
    async with session_factory() as session:
        user = await UserRepository(session).get_by_id(db_user.id)
        paid = await has_paid_pro(session, db_user.id)
        if user and not user.trial_pro_used and not paid:
            days = get_settings().trial_pro_days
            trial_line = muted(f"🎁 Trial PRO {days} дн. — кнопка на сводке")
    return build_subscription_hub(pricing, access_line=access, trial_line=trial_line)


async def _subscription_status_text(db_user: DbUser) -> str:
    session_factory = get_session_factory()
    async with session_factory() as session:
        user = await UserRepository(session).get_by_id(db_user.id)
        subscription = await get_effective_subscription(session, db_user.id)
        remaining = await remaining_generations_today(session, db_user.id)
        tier_line = await describe_access_tier(session, user, subscription) if user else None
    if user is None:
        return "Ошибка профиля."
    return build_my_access_text(
        user,
        subscription,
        generations_remaining=remaining,
        access_tier_line=tier_line,
    )


async def _notify_admins_qr(
    bot: Bot,
    *,
    subscription_id: int,
    db_user: DbUser,
    plan: SubscriptionPlan,
    kind: str = "QR",
) -> None:
    settings = get_settings()
    if not settings.admin_ids:
        return
    plan_name = "PRO" if plan == SubscriptionPlan.PRO else "Lite"
    text = (
        f"<b>Заявка на оплату ({kind})</b>\n\n"
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
    pricing = await get_subscription_pricing()
    text = await _subscription_hub_text(db_user, pricing)
    await message.answer(text, reply_markup=subscription_hub_keyboard(pricing))


@router.callback_query(F.data == "menu:subscription")
async def menu_subscription(callback: CallbackQuery, db_user: DbUser) -> None:
    pricing = await get_subscription_pricing()
    text = await _subscription_hub_text(db_user, pricing)
    await answer_and_edit(callback, text, reply_markup=subscription_hub_keyboard(pricing))


@router.callback_query(F.data == "sub:status")
async def subscription_status(callback: CallbackQuery, db_user: DbUser) -> None:
    text = await _subscription_status_text(db_user)
    await answer_and_edit(callback, text, reply_markup=subscription_subscreen_keyboard())


@router.callback_query(F.data == "sub:compare")
async def subscription_compare(callback: CallbackQuery) -> None:
    await answer_and_edit(
        callback,
        PLANS_COMPARISON_TEXT,
        reply_markup=subscription_subscreen_keyboard(),
    )


@router.callback_query(F.data == "sub:calc")
async def subscription_calculator_table(callback: CallbackQuery) -> None:
    pricing = await get_subscription_pricing()
    await answer_and_edit(
        callback,
        build_calculator_table(pricing),
        reply_markup=calculator_volumes_keyboard(),
    )


@router.callback_query(F.data.regexp(r"^sub:calc:\d+$"))
async def subscription_calculator_volume(callback: CallbackQuery) -> None:
    volume = int(callback.data.split(":")[-1])
    pricing = await get_subscription_pricing()
    await answer_and_edit(
        callback,
        build_calculator_detail(pricing, volume),
        reply_markup=calculator_detail_keyboard(volume=volume, pricing=pricing),
    )


@router.callback_query(F.data == "sub:pay:menu")
async def payment_methods_menu(callback: CallbackQuery) -> None:
    pricing = await get_subscription_pricing()
    await answer_and_edit(
        callback,
        build_payment_hub(pricing),
        reply_markup=payment_methods_keyboard(),
    )


@router.callback_query(F.data == "sub:pay:crypto")
async def payment_crypto_plans(callback: CallbackQuery) -> None:
    pricing = await get_subscription_pricing()
    settings = get_settings()
    if not crypto_pay_enabled(settings):
        await callback.answer("Crypto Bot не настроен", show_alert=True)
        return
    await answer_and_edit(
        callback,
        "🪙 <b>Crypto Bot</b>\n\nВыберите тариф. Оплата в @CryptoBot (USDT, TON и др.).",
        reply_markup=crypto_plan_keyboard(pricing),
    )


@router.callback_query(F.data == "sub:pay:card")
async def payment_card_hub(callback: CallbackQuery) -> None:
    pricing = await get_subscription_pricing()
    settings = get_settings()
    if stars_payments_enabled(settings):
        body = (
            "💳 <b>Карта · РФ / РБ</b>\n\n"
            "Оплата через Telegram Stars или перевод по реквизитам (СБП / ERIP)."
        )
    elif card_payments_enabled(settings):
        body = (
            "💳 <b>Карта · РФ / РБ</b>\n\n"
            f"Оплата картой в Telegram ({payment_mode_label(settings)}) "
            "или перевод физ. лица по реквизитам."
        )
    else:
        body = (
            "💳 <b>Карта · РФ / РБ</b>\n\n"
            "Перевод с карты / СБП / ERIP по реквизитам. После оплаты — «Я оплатил»."
        )
    await answer_and_edit(callback, body, reply_markup=card_payment_keyboard(pricing))


@router.callback_query(F.data == "sub:pay:transfer")
async def payment_transfer_plans(callback: CallbackQuery) -> None:
    pricing = await get_subscription_pricing()
    await answer_and_edit(
        callback,
        "📋 <b>СБП / перевод (РФ / РБ)</b>\n\n"
        f"{pricing.lite_line()}\n{pricing.pro_line()}",
        reply_markup=qr_plan_keyboard(pricing),
    )


@router.callback_query(F.data == "sub:pay:legal")
async def payment_legal_plans(callback: CallbackQuery) -> None:
    pricing = await get_subscription_pricing()
    await answer_and_edit(
        callback,
        "🏦 <b>Безнал · юр. лицо</b>\n\n"
        "Счёт на организацию (РФ / РБ). Выберите тариф:",
        reply_markup=legal_plan_keyboard(pricing),
    )


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
        await message.answer("Ошибка привязки платёжа.")
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
        f"Действует до: <b>{expires}</b>\n\n"
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
                await safe_edit_message(
                    callback.message,
                    f"Crypto Bot: {exc}",
                    reply_markup=payment_methods_keyboard(),
                )
            return
        subscription.external_payment_id = str(invoice.get("invoice_id", ""))
        await session.commit()

    pay_url = invoice.get("bot_invoice_url") or invoice.get("pay_url") or invoice.get("mini_app_invoice_url")
    if not pay_url:
        await callback.answer("Нет ссылки на оплату", show_alert=True)
        return
    pricing = await get_subscription_pricing()
    plan_name = "PRO" if plan == SubscriptionPlan.PRO else "Lite"
    usd = pricing.pro_usd if plan == SubscriptionPlan.PRO else pricing.lite_usd
    await callback.answer()
    if callback.message:
        await safe_edit_message(
            callback.message,
            f"🪙 <b>Оплата {plan_name}</b>\n\n"
            f"Сумма: <b>{pricing.format_usd_line(usd)}</b>\n"
            "<i>Оплата USDT, TON и др. в @CryptoBot</i>\n\n"
            "После оплаты доступ включится автоматически (до 2 минут).",
            reply_markup=crypto_pay_keyboard(str(pay_url)),
        )


@router.callback_query(F.data == "sub:crypto:check")
async def crypto_check_payment(callback: CallbackQuery, bot: Bot, db_user: DbUser) -> None:
    await callback.answer("Проверяю…")
    await process_crypto_pending_once(bot)
    pricing = await get_subscription_pricing()
    text = await _subscription_status_text(db_user)
    if callback.message:
        await safe_edit_message(
            callback.message, text, reply_markup=subscription_menu_keyboard(pricing)
        )


@router.callback_query(F.data == "sub:qr:menu")
async def qr_plan_menu(callback: CallbackQuery) -> None:
    pricing = await get_subscription_pricing()
    await answer_and_edit(
        callback,
        "📋 <b>СБП / перевод (РФ / РБ)</b>\n\n"
        f"{pricing.lite_line()}\n{pricing.pro_line()}",
        reply_markup=qr_plan_keyboard(pricing),
    )


@router.callback_query(F.data.in_({"sub:qr:lite", "sub:qr:pro"}))
async def qr_show_instructions(callback: CallbackQuery) -> None:
    plan_key = callback.data.split(":")[-1]
    plan = SubscriptionPlan.PRO if plan_key == "pro" else SubscriptionPlan.LITE
    settings = get_settings()
    pricing = await get_subscription_pricing()
    await answer_and_edit(
        callback,
        qr_instructions(settings, plan, pricing=pricing),
        reply_markup=qr_paid_keyboard(plan_key),
    )


@router.callback_query(F.data.in_({"sub:legal:lite", "sub:legal:pro"}))
async def legal_show_instructions(callback: CallbackQuery) -> None:
    plan_key = callback.data.split(":")[-1]
    plan = SubscriptionPlan.PRO if plan_key == "pro" else SubscriptionPlan.LITE
    settings = get_settings()
    pricing = await get_subscription_pricing()
    await answer_and_edit(
        callback,
        legal_payment_instructions(settings, plan, pricing=pricing),
        reply_markup=legal_paid_keyboard(plan_key),
    )


@router.callback_query(F.data.startswith("sub:legal:paid:"))
async def legal_mark_paid(callback: CallbackQuery, bot: Bot, db_user: DbUser) -> None:
    plan_key = callback.data.split(":")[-1]
    plan = SubscriptionPlan.PRO if plan_key == "pro" else SubscriptionPlan.LITE
    session_factory = get_session_factory()
    async with session_factory() as session:
        subscription = await create_qr_pending(session, user_id=db_user.id, plan=plan)
        await session.commit()
        sub_id = subscription.id

    await _notify_admins_qr(
        bot, subscription_id=sub_id, db_user=db_user, plan=plan, kind="Безнал юр."
    )
    pricing = await get_subscription_pricing()
    await callback.answer("Заявка отправлена")
    if callback.message:
        await safe_edit_message(
            callback.message,
            "✅ Заявка на оплату по счёту создана.\n\n"
            f"Номер: <code>{sub_id}</code>\n"
            "После проверки платежа администратор активирует подписку.",
            reply_markup=subscription_menu_keyboard(pricing),
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
    pricing = await get_subscription_pricing()
    await callback.answer("Заявка отправлена администратору")
    if callback.message:
        await safe_edit_message(
            callback.message,
            "✅ Заявка на оплату QR создана.\n\n"
            f"Номер заявки: <code>{sub_id}</code>\n"
            "После проверки перевода администратор активирует подписку.",
            reply_markup=subscription_menu_keyboard(pricing),
        )
