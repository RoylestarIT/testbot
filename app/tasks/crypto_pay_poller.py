from __future__ import annotations

import asyncio

from aiogram import Bot
from loguru import logger
from sqlalchemy import select

from app.core.config import Settings, get_settings
from app.db.models import PaymentMethod, Subscription, SubscriptionStatus, User
from app.db.session import get_session_factory
from app.services.payment.crypto_notify import notify_crypto_paid
from app.services.payment.crypto_pay import crypto_pay_enabled, get_invoices
from app.services.subscription import activate_from_crypto_invoice, expire_pending_crypto

POLL_INTERVAL_SEC = 90


async def process_crypto_pending_once(bot: Bot, settings: Settings | None = None) -> None:
    if not crypto_pay_enabled(settings):
        return
    settings = settings or get_settings()
    session_factory = get_session_factory()

    async with session_factory() as session:
        result = await session.execute(
            select(Subscription.id, Subscription.external_payment_id, User.tg_id)
            .join(User, Subscription.user_id == User.id)
            .where(
                Subscription.status == SubscriptionStatus.PENDING,
                Subscription.payment_method == PaymentMethod.CRYPTO,
                Subscription.external_payment_id.isnot(None),
            )
        )
        pending = {
            int(invoice_id): (subscription_id, tg_id)
            for subscription_id, invoice_id, tg_id in result.all()
            if invoice_id and str(invoice_id).isdigit()
        }
    if not pending:
        return

    try:
        invoices = await get_invoices(settings, list(pending))
    except Exception as exc:
        logger.warning("crypto getInvoices failed count={} err={}", len(pending), exc)
        return

    for invoice_id, invoice in invoices.items():
        if invoice_id not in pending:
            continue
        subscription_id, tg_id = pending[invoice_id]
        status = invoice.get("status")
        async with session_factory() as session:
            if status == "expired":
                if await expire_pending_crypto(session, subscription_id):
                    await session.commit()
                    logger.info("crypto pending expired sub_id={} invoice={}", subscription_id, invoice_id)
                continue
            if status != "paid":
                continue
            activated = await activate_from_crypto_invoice(
                session, subscription_id=subscription_id, invoice_id=str(invoice_id)
            )
            if activated is None:
                continue
            await session.commit()
        await notify_crypto_paid(bot, tg_id, activated)


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
        await asyncio.sleep(POLL_INTERVAL_SEC)
