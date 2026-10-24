from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.core.config import get_settings
from app.db.models import SubscriptionPlan
from app.services.payment.fx_rates import SubscriptionPricing
from app.services.payment.payment_options import stars_payments_enabled
from app.services.payment.subscription_calculator import PRESET_VOLUMES, suggest_plan_for_volume
from app.services.payment.telegram_stars import effective_stars_amount


def calculator_volumes_keyboard(
    *,
    last_volume: int | None = None,
    show_table_link: bool = True,
) -> InlineKeyboardMarkup:
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
    if show_table_link:
        rows.append(
            [InlineKeyboardButton(text="📊 Полная таблица", callback_data="sub:calc:table")]
        )
    rows.append([InlineKeyboardButton(text="◀️ Подписка", callback_data="menu:subscription")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _calc_pay_button_label(pricing: SubscriptionPricing, *, pro: bool) -> str:
    settings = get_settings()
    rub = pricing.pro_rub if pro else pricing.lite_rub
    icon = "🚀 PRO" if pro else "✨ Lite"
    label = f"{icon} {rub:,}".replace(",", " ") + " ₽"
    if stars_payments_enabled(settings):
        stars = effective_stars_amount(
            settings, SubscriptionPlan.PRO if pro else SubscriptionPlan.LITE
        )
        label = f"{icon} {rub:,}".replace(",", " ") + f" ₽ · {stars} ⭐"
    return label


def calculator_detail_keyboard(*, volume: int, pricing: SubscriptionPricing) -> InlineKeyboardMarkup:
    plan = suggest_plan_for_volume(volume, pricing)
    lite_btn = InlineKeyboardButton(
        text=_calc_pay_button_label(pricing, pro=False),
        callback_data="sub:pay:menu",
    )
    pro_btn = InlineKeyboardButton(
        text=_calc_pay_button_label(pricing, pro=True),
        callback_data="sub:pay:menu",
    )
    if plan == "pro":
        pay_row = [pro_btn, lite_btn]
    else:
        pay_row = [lite_btn, pro_btn]
    return InlineKeyboardMarkup(
        inline_keyboard=[
            pay_row,
            [
                InlineKeyboardButton(text="◀️ К калькулятору", callback_data="sub:calc"),
                InlineKeyboardButton(text="📊 Таблица", callback_data="sub:calc:table"),
            ],
            [InlineKeyboardButton(text="◀️ Подписка", callback_data="menu:subscription")],
        ]
    )
