from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.bot.legal.documents import LegalDocKind, page_count
from app.core.config import Settings, get_settings


def legal_document_keyboard(
    kind: LegalDocKind,
    page_index: int,
    *,
    settings: Settings | None = None,
    show_back_to_accept: bool = True,
) -> InlineKeyboardMarkup:
    settings = settings or get_settings()
    total = page_count(kind, settings)
    page_index = max(0, min(page_index, total - 1))

    nav_row: list[InlineKeyboardButton] = []
    if total > 1:
        if page_index > 0:
            nav_row.append(
                InlineKeyboardButton(
                    text="◀️",
                    callback_data=f"legal:{kind.value}:{page_index - 1}",
                )
            )
        else:
            nav_row.append(InlineKeyboardButton(text="·", callback_data="legal:noop"))
        nav_row.append(
            InlineKeyboardButton(
                text=f"{page_index + 1}/{total}",
                callback_data="legal:noop",
            )
        )
        if page_index < total - 1:
            nav_row.append(
                InlineKeyboardButton(
                    text="▶️",
                    callback_data=f"legal:{kind.value}:{page_index + 1}",
                )
            )
        else:
            nav_row.append(InlineKeyboardButton(text="·", callback_data="legal:noop"))

    rows: list[list[InlineKeyboardButton]] = []
    if nav_row:
        rows.append(nav_row)

    link_row: list[InlineKeyboardButton] = []
    if kind is LegalDocKind.PRIVACY and settings.terms_of_service_url.strip():
        link_row.append(
            InlineKeyboardButton(text="📜 Условия на сайте", url=settings.terms_of_service_url.strip())
        )
    elif kind is LegalDocKind.TERMS and settings.privacy_policy_url.strip():
        link_row.append(
            InlineKeyboardButton(text="🔒 Политика на сайте", url=settings.privacy_policy_url.strip())
        )
    if link_row:
        rows.append(link_row)

    if show_back_to_accept:
        rows.append([InlineKeyboardButton(text="◀️ К экрану принятия", callback_data="legal:back:accept")])

    return InlineKeyboardMarkup(inline_keyboard=rows)


def legal_open_from_terms_row() -> list[InlineKeyboardButton]:
    """Кнопки чтения документов внутри бота (экран «Принимаю»)."""
    return [
        InlineKeyboardButton(text="🔒 Конфиденциальность", callback_data="legal:privacy:0"),
        InlineKeyboardButton(text="📜 Полные условия", callback_data="legal:terms:0"),
    ]
