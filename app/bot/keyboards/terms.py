from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.core.config import get_settings


def terms_acceptance_keyboard() -> InlineKeyboardMarkup:
    settings = get_settings()
    rows: list[list[InlineKeyboardButton]] = []
    link_row: list[InlineKeyboardButton] = []
    if settings.privacy_policy_url.strip():
        link_row.append(
            InlineKeyboardButton(text="🔒 Конфиденциальность", url=settings.privacy_policy_url.strip())
        )
    if settings.terms_of_service_url.strip():
        link_row.append(
            InlineKeyboardButton(text="📜 Полные условия", url=settings.terms_of_service_url.strip())
        )
    if link_row:
        rows.append(link_row)
    rows.append([InlineKeyboardButton(text="✅ Принимаю", callback_data="onboarding:accept")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
