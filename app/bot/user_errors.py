from __future__ import annotations

from dataclasses import dataclass

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

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
                    [("🔄 Sync", "review:sync")],
                ),
            )
        if code == 429:
            return UserFacingError(
                "⏳ <b>Слишком много запросов к API</b>\n\n"
                "Подождите 1–2 минуты и нажмите Sync снова.",
                reply_markup=_kb([("🔄 Sync", "review:sync")]),
            )
        return UserFacingError(
            f"🛒 <b>Ошибка маркетплейса</b>\n\n{exc}\n\n"
            "Если повторяется — напишите в поддержку с временем ошибки.",
            reply_markup=_kb(
                [("🔄 Sync", "review:sync")],
                [("🆘 Поддержка", "support:write")],
            ),
        )
    if isinstance(exc, LLMError):
        return UserFacingError(
            f"🤖 <b>Генерация временно недоступна</b>\n\n{exc}\n\n"
            "Проверьте лимит тарифа или попробуйте позже.",
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
