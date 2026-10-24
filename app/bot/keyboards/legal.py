from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.bot.legal.documents import LegalDocKind, page_count
from app.core.config import Settings, get_settings

LegalBack = str  # "a" accept | "m" menu | "s" support

_BACK_ACCEPT = "a"
_BACK_MENU = "m"
_BACK_SUPPORT = "s"


def _page_callback(kind: LegalDocKind, page: int, back: LegalBack) -> str:
    if back == _BACK_ACCEPT:
        return f"legal:{kind.value}:{page}"
    return f"legal:{kind.value}:{page}:{back}"


def parse_legal_back(data: str) -> LegalBack:
    parts = data.split(":")
    if len(parts) >= 4 and parts[0] == "legal" and parts[3] in (_BACK_MENU, _BACK_SUPPORT):
        return parts[3]
    return _BACK_ACCEPT


def legal_hub_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            legal_open_from_terms_row(back=_BACK_MENU),
            [InlineKeyboardButton(text="◀️ Назад", callback_data="menu:more")],
        ]
    )


def legal_document_keyboard(
    kind: LegalDocKind,
    page_index: int,
    *,
    settings: Settings | None = None,
    back: LegalBack = _BACK_ACCEPT,
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
                    callback_data=_page_callback(kind, page_index - 1, back),
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
                    callback_data=_page_callback(kind, page_index + 1, back),
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

    if back == _BACK_ACCEPT:
        rows.append([InlineKeyboardButton(text="◀️ К экрану принятия", callback_data="legal:back:accept")])
    elif back == _BACK_SUPPORT:
        rows.append([InlineKeyboardButton(text="◀️ Поддержка", callback_data="legal:back:support")])
    else:
        rows.append([InlineKeyboardButton(text="◀️ К документам", callback_data="legal:back:menu")])

    return InlineKeyboardMarkup(inline_keyboard=rows)


def legal_open_from_terms_row(*, back: LegalBack = _BACK_ACCEPT) -> list[InlineKeyboardButton]:
    """Кнопки чтения документов внутри бота."""
    if back == _BACK_ACCEPT:
        return [
            InlineKeyboardButton(text="🔒 Конфиденциальность", callback_data="legal:privacy:0"),
            InlineKeyboardButton(text="📜 Полные условия", callback_data="legal:terms:0"),
        ]
    return [
        InlineKeyboardButton(
            text="🔒 Конфиденциальность",
            callback_data=f"legal:privacy:0:{back}",
        ),
        InlineKeyboardButton(
            text="📜 Полные условия",
            callback_data=f"legal:terms:0:{back}",
        ),
    ]
