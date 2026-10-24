from __future__ import annotations

from aiogram import Bot
from loguru import logger

from app.db.models import Subscription
from app.services.subscription import plan_label


def crypto_paid_text(activated: Subscription) -> str:
    expires = activated.expires_at.strftime("%d.%m.%Y") if activated.expires_at else "—"
    return (
        "✅ Оплата Crypto Bot принята!\n\n"
        f"Тариф: <b>{plan_label(activated.plan)}</b>\n"
        f"Действует до: <b>{expires}</b>"
    )


async def notify_crypto_paid(bot: Bot, tg_id: int, activated: Subscription) -> None:
    try:
        await bot.send_message(tg_id, crypto_paid_text(activated))
    except Exception:
        logger.warning("Failed to notify tg_id={} about crypto payment", tg_id)
