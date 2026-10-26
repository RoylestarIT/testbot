from __future__ import annotations

from dataclasses import dataclass

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.bot.ui import SYNC_BUTTON
from app.services.llm import LLMError
from app.services.marketplace.base import MarketplaceAPIError
from app.core.security import EncryptionError


@dataclass(frozen=True, slots=True)
class UserFacingError:
    html: str
    reply_markup: InlineKeyboardMarkup | None = None


def _kb(*rows: list[tuple[str, str]]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=label, callback_data=data) for label, data in row]
            for row in rows
        ]
    )


def user_error_from_exception(exc: BaseException) -> UserFacingError:
    if isinstance(exc, EncryptionError):
        return UserFacingError(
            "🔐 <b>Не удалось прочитать API-ключ</b>\n\n"
            "Ключ сохранён в другом окружении или повреждён. "
            "Подключите кабинет заново в ⚙️ Настройки.",
            reply_markup=_kb(
                [("⚙️ Настройки", "menu:settings"), ("🩺 Здоровье", "menu:service_status")],
                [("🆘 Поддержка", "menu:support")],
            ),
        )
    if isinstance(exc, MarketplaceAPIError):
        code = exc.status_code
        if code == 401:
            return UserFacingError(
                "🔑 <b>Маркетплейс отклонил ключ</b>\n\n"
                "Проверьте API-ключ в личном кабинете WB/Ozon и обновите его в настройках.",
                reply_markup=_kb(
                    [("⚙️ Кабинеты", "menu:settings")],
                    [(SYNC_BUTTON, "review:sync")],
                ),
            )
        if code == 429:
            return UserFacingError(
                "⏳ <b>Слишком много запросов к API</b>\n\n"
                f"Подождите 1–2 минуты и нажмите «{SYNC_BUTTON}» снова.",
                reply_markup=_kb([(SYNC_BUTTON, "review:sync")]),
            )
        return UserFacingError(
            f"🛒 <b>Ошибка маркетплейса</b>\n\n{exc}\n\n"
            "Если повторяется — напишите в поддержку с временем ошибки.",
            reply_markup=_kb(
                [(SYNC_BUTTON, "review:sync")],
                [("🆘 Поддержка", "support:write")],
            ),
        )
    if isinstance(exc, LLMError):
        hint = (
            "Если лимит не исчерпан — обычно это настройка ключа OpenAI на сервере."
            if "OPENAI" in str(exc) or "ключ" in str(exc).lower()
            else "Проверьте лимит тарифа или попробуйте позже."
        )
        return UserFacingError(
            f"🤖 <b>Генерация временно недоступна</b>\n\n{exc}\n\n{hint}",
            reply_markup=_kb(
                [("💎 Подписка", "menu:subscription")],
                [("📬 Очередь", "review:mp:list")],
            ),
        )
    return UserFacingError(
        "⚠️ <b>Что-то пошло не так</b>\n\n"
        "Попробуйте ещё раз. Если не помогло — поддержка поможет с контекстом.",
        reply_markup=_kb(
            [("🏠 Сводка", "menu:dashboard")],
            [("🆘 Поддержка", "support:write")],
        ),
    )
