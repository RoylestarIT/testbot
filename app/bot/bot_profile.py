"""Профиль бота в Telegram (описание, команды) — выставляется при старте."""

from __future__ import annotations

from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats, BotCommandScopeChat
from loguru import logger

from app.bot.ui import BRAND
from app.core.config import Settings

# Лимиты Telegram Bot API
SHORT_DESCRIPTION_MAX = 120
DESCRIPTION_MAX = 512

DEFAULT_SHORT_DESCRIPTION = (
    f"{BRAND}: ответы на отзывы WB/Ozon в Telegram. Очередь, 3 варианта, PRO — publish. ~$10 / ~$20."
)

DEFAULT_DESCRIPTION = (
    f"{BRAND} — co-pilot для селлеров Wildberries и Ozon.\n\n"
    "• Sync отзывов в очередь в Telegram\n"
    "• 3 варианта ответа и ваш tone of voice\n"
    "• 1–3★ — только вы подтверждаете текст\n"
    "• PRO: publish в API и авто-ответы 4–5★\n\n"
    "Lite ~$10 / PRO ~$20 в месяц. Crypto Bot, карта/перевод РФ·РБ, безнал для юр. лиц.\n\n"
    "/start — сводка · /help — справка · /my_subscription — тариф"
)


def resolve_short_description(settings: Settings) -> str:
    custom = settings.bot_short_description.strip()
    text = custom if custom else DEFAULT_SHORT_DESCRIPTION
    if len(text) > SHORT_DESCRIPTION_MAX:
        return text[: SHORT_DESCRIPTION_MAX - 1] + "…"
    return text


def resolve_description(settings: Settings) -> str:
    custom = settings.bot_description.strip()
    text = custom if custom else DEFAULT_DESCRIPTION
    if len(text) > DESCRIPTION_MAX:
        return text[: DESCRIPTION_MAX - 3] + "…"
    return text


def default_bot_commands() -> list[BotCommand]:
    return [
        BotCommand(command="start", description="🏠 Сводка WB/Ozon"),
        BotCommand(command="dashboard", description="📊 Статус и очередь"),
        BotCommand(command="help", description="📖 Справка"),
        BotCommand(command="my_subscription", description="💎 Подписка Lite/PRO"),
        BotCommand(command="promo", description="🎟 Промокод"),
    ]


def admin_bot_commands() -> list[BotCommand]:
    return default_bot_commands() + [
        BotCommand(command="admin", description="🛠 Админ-панель"),
    ]


async def apply_bot_profile(bot: Bot, settings: Settings) -> None:
    lang = settings.bot_profile_language.strip() or None
    short_desc = resolve_short_description(settings)
    description = resolve_description(settings)

    try:
        await bot.set_my_short_description(short_desc, language_code=lang)
        await bot.set_my_description(description, language_code=lang)
        logger.info(
            "Bot profile updated lang={} short_len={} desc_len={}",
            lang or "default",
            len(short_desc),
            len(description),
        )
    except Exception as exc:
        logger.warning("Failed to set bot description: {}", exc)

    try:
        await bot.set_my_commands(default_bot_commands(), scope=BotCommandScopeAllPrivateChats())
        for admin_id in settings.admin_ids:
            try:
                await bot.set_my_commands(
                    admin_bot_commands(),
                    scope=BotCommandScopeChat(chat_id=admin_id),
                )
            except Exception as exc:
                logger.warning("Admin commands for tg_id={} failed: {}", admin_id, exc)
        logger.info("Bot commands registered (admins={})", len(settings.admin_ids))
    except Exception as exc:
        logger.warning("Failed to set bot commands: {}", exc)
