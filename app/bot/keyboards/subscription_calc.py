from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.services.payment.subscription_calculator import PRESET_VOLUMES, suggest_plan_for_volume
from app.services.payment.fx_rates import SubscriptionPricing


def calculator_volumes_keyboard(*, last_volume: int | None = None) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    if last_volume and last_volume in PRESET_VOLUMES:
        rows.append(
            [
                InlineKeyboardButton(
                    text=f"🔁 {last_volume} отв. (как в прошлый раз)",
                    callback_data=f"sub:calc:{last_volume}",
                )
            ]
        )
    chunk: list[InlineKeyboardButton] = []
    for vol in PRESET_VOLUMES:
        chunk.append(
            InlineKeyboardButton(text=f"{vol} отв.", callback_data=f"sub:calc:{vol}")
        )
        if len(chunk) == 2:
            rows.append(chunk)
            chunk = []
    if chunk:
        rows.append(chunk)
    rows.append([InlineKeyboardButton(text="◀️ Подписка", callback_data="menu:subscription")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def calculator_detail_keyboard(*, volume: int, pricing: SubscriptionPricing) -> InlineKeyboardMarkup:
    plan = suggest_plan_for_volume(volume, pricing)
    primary = (
        InlineKeyboardButton(text="🚀 Оформить PRO", callback_data="sub:pay:menu")
        if plan == "pro"
        else InlineKeyboardButton(text="✨ Оформить Lite", callback_data="sub:pay:menu")
    )
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [primary],
            [InlineKeyboardButton(text="◀️ К таблице", callback_data="sub:calc")],
            [InlineKeyboardButton(text="◀️ Подписка", callback_data="menu:subscription")],
        ]
    )
