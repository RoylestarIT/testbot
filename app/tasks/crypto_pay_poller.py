from __future__ import annotations

import asyncio

from aiogram import Bot
from loguru import logger
from sqlalchemy import select

from app.core.config import Settings, get_settings
from app.db.models import PaymentMethod, Subscription, SubscriptionStatus, User
from app.db.session import get_session_factory
from app.services.payment.crypto_pay import crypto_pay_enabled, get_invoice
from app.services.subscription import activate_from_crypto_invoice


async def _notify_paid(bot: Bot, tg_id: int, plan_name: str, expires: str) -> None:
    try:
        await bot.send_message(
            tg_id,
            f"✅ Оплата Crypto Bot принята!\n\n"
            f"Тариф: <b>{plan_name}</b>\n"
            f"Активна до: <b>{expires}</b>",
        )
    except Exception:
        logger.warning("Failed to notify tg_id={} about crypto payment", tg_id)


async def process_crypto_pending_once(bot: Bot, settings: Settings | None = None) -> None:
    if not crypto_pay_enabled(settings):
        return
    settings = settings or get_settings()
    session_factory = get_session_factory()

    async with session_factory() as session:
        result = await session.execute(
            select(Subscription, User)
            .join(User, Subscription.user_id == User.id)
            .where(
                Subscription.status == SubscriptionStatus.PENDING,
                Subscription.payment_method == PaymentMethod.CRYPTO,
                Subscription.external_payment_id.isnot(None),
            )
        )
        rows = result.all()

    for subscription, user in rows:
        invoice_id_raw = subscription.external_payment_id
        if not invoice_id_raw or not str(invoice_id_raw).isdigit():
            continue
        try:
            invoice = await get_invoice(settings, int(invoice_id_raw))
        except Exception as exc:
            logger.warning("crypto getInvoice failed sub_id={} err={}", subscription.id, exc)
            continue
        if invoice is None or invoice.get("status") != "paid":
            continue
        async with session_factory() as session:
            activated = await activate_from_crypto_invoice(
                session,
                subscription_id=subscription.id,
                invoice_id=str(invoice.get("invoice_id", invoice_id_raw)),
            )
            if activated is None:
                continue
            await session.commit()
            expires = activated.expires_at.strftime("%d.%m.%Y") if activated.expires_at else "—"
            plan_name = "PRO" if activated.plan.value == "pro" else "Lite"
        await _notify_paid(bot, user.tg_id, plan_name, expires)


async def crypto_pay_poller_loop(bot: Bot, settings: Settings | None = None) -> None:
    settings = settings or get_settings()
    if not crypto_pay_enabled(settings):
        logger.info("Crypto Pay poller disabled (no token)")
        return
    logger.info("Crypto Pay poller started")
    while True:
        try:
            await process_crypto_pending_once(bot, settings)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Crypto Pay poller iteration failed")
        await asyncio.sleep(90)
