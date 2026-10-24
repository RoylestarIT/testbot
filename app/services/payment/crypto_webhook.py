from __future__ import annotations

import json

from aiohttp import web
from aiogram import Bot
from loguru import logger

from app.core.config import Settings, get_settings
from app.db.repositories.user import UserRepository
from app.db.session import get_session_factory
from app.services.payment.crypto_notify import notify_crypto_paid
from app.services.payment.crypto_pay import parse_invoice_payload, verify_webhook_signature
from app.services.subscription import activate_from_crypto_invoice


async def handle_crypto_webhook(request: web.Request) -> web.Response:
    bot: Bot | None = request.app.get("bot")
    settings: Settings = request.app.get("settings") or get_settings()
    token = settings.crypto_pay_api_token.strip()
    if not token:
        return web.Response(status=503, text="crypto disabled")

    body_raw = await request.read()
    signature = request.headers.get("Crypto-Pay-API-Signature")
    if not verify_webhook_signature(token, body_raw, signature):
        logger.warning("Crypto Pay webhook: bad signature")
        return web.Response(status=403, text="forbidden")

    try:
        update = json.loads(body_raw.decode())
    except json.JSONDecodeError:
        return web.Response(status=400, text="bad json")

    if update.get("update_type") != "invoice_paid":
        return web.Response(text="ok")

    invoice = update.get("payload") or {}
    payload_data = parse_invoice_payload(invoice.get("payload"))
    if payload_data is None:
        logger.warning("Crypto webhook: missing payload")
        return web.Response(text="ok")

    try:
        subscription_id = int(payload_data.get("subscription_id", 0))
    except (TypeError, ValueError):
        logger.warning("Crypto webhook: bad subscription_id in payload")
        return web.Response(text="ok")
    if subscription_id <= 0:
        return web.Response(text="ok")

    invoice_id = str(invoice.get("invoice_id", ""))
    session_factory = get_session_factory()
    async with session_factory() as session:
        activated = await activate_from_crypto_invoice(
            session,
            subscription_id=subscription_id,
            invoice_id=invoice_id,
        )
        if activated is None:
            return web.Response(text="ok")
        user = await UserRepository(session).get_by_id(activated.user_id)
        await session.commit()

    if bot and user:
        await notify_crypto_paid(bot, user.tg_id, activated)

    return web.Response(text="ok")


def register_crypto_webhook_routes(app: web.Application, *, bot: Bot, settings: Settings | None = None) -> None:
    settings = settings or get_settings()
    app["bot"] = bot
    app["settings"] = settings
    path = settings.crypto_pay_webhook_path.strip() or "/cryptopay/webhook"
    app.router.add_post(path, handle_crypto_webhook)
    logger.info("Crypto Pay webhook registered at POST {}", path)
