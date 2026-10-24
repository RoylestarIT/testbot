from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.bot.keyboards.legal import legal_open_from_terms_row
from app.core.config import get_settings


def terms_acceptance_keyboard() -> InlineKeyboardMarkup:
    settings = get_settings()
    rows: list[list[InlineKeyboardButton]] = [legal_open_from_terms_row()]

    extra_links: list[InlineKeyboardButton] = []
    if settings.privacy_policy_url.strip():
        extra_links.append(
            InlineKeyboardButton(text="🌐 Политика (сайт)", url=settings.privacy_policy_url.strip())
        )
    if settings.terms_of_service_url.strip():
        extra_links.append(
            InlineKeyboardButton(text="🌐 Условия (сайт)", url=settings.terms_of_service_url.strip())
        )
    if extra_links:
        rows.append(extra_links)

    rows.append([InlineKeyboardButton(text="✅ Принимаю", callback_data="onboarding:accept")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
