from __future__ import annotations

from app.bot.ui import brand_title, bullet, muted, section
from app.services.payment.fx_rates import SubscriptionPricing, _fmt_rub

# Типичный рынок «оплата за ответ» (без имён сервисов)
PER_ANSWER_RUB_LOW = 1.0
PER_ANSWER_RUB_MID = 2.0
PER_ANSWER_RUB_HIGH = 3.0

PRESET_VOLUMES = (100, 200, 300, 500, 800, 1000)


def suggest_plan_for_volume(volume: int, pricing: SubscriptionPricing) -> str:
    """lite | pro — подсказка для кнопок оплаты."""
    lite_rub = pricing.lite_rub
    pro_rub = pricing.pro_rub
    mid_market = _pay_per_answer_total(volume, PER_ANSWER_RUB_MID)
    if mid_market > pro_rub or volume >= 800:
        return "pro"
    if mid_market > lite_rub or volume >= 400:
        return "lite"
    return "lite"


def _pay_per_answer_total(volume: int, rub_per_answer: float) -> int:
    return int(round(volume * rub_per_answer))


def _best_plan_hint(
    volume: int,
    *,
    lite_rub: int,
    pro_rub: int,
) -> str:
    mid_market = _pay_per_answer_total(volume, PER_ANSWER_RUB_MID)
    if mid_market <= lite_rub:
        return "На этом объёме pay-per-answer часто дешевле — мы честно показываем цифры."
    if lite_rub < mid_market:
        if pro_rub < _pay_per_answer_total(volume, PER_ANSWER_RUB_HIGH):
            return f"✨ <b>Lite</b> выгоднее рынка ~{PER_ANSWER_RUB_MID:g} ₽/ответ; 🚀 <b>PRO</b> — при объёме и publish."
        return f"✨ <b>Lite</b> выгоднее pay-per-answer при ~{volume} ответах/мес."
    return ""


def _volume_overview_line(vol: int, *, lite_rub: int, pro_rub: int) -> str:
    low = _pay_per_answer_total(vol, PER_ANSWER_RUB_LOW)
    high = _pay_per_answer_total(vol, PER_ANSWER_RUB_HIGH)
    mid = _pay_per_answer_total(vol, PER_ANSWER_RUB_MID)
    hint = ""
    if mid > lite_rub:
        hint = " → ✨ Lite"
    elif mid > pro_rub:
        hint = " → 🚀 PRO"
    return bullet(
        f"<b>{vol}</b> отв./мес · рынок {_fmt_rub(low)}–{_fmt_rub(high)}{hint}"
    )


def build_calculator_table(pricing: SubscriptionPricing) -> str:
    lite_rub = pricing.lite_rub
    pro_rub = pricing.pro_rub
    from app.bot.subscription_ui import SUBSCRIPTION_SEP

    lines = [
        brand_title("Калькулятор", tagline="Подписка vs ₽ за ответ", icon="🧮").strip(),
        SUBSCRIPTION_SEP,
        "",
        section("Фикс в месяц", icon="💎"),
        "",
        bullet(f"Lite — <b>{_fmt_rub(lite_rub)}</b>"),
        bullet(f"PRO — <b>{_fmt_rub(pro_rub)}</b>"),
        "",
        section("Pay-per-answer на рынке", icon="💸"),
        "",
        muted(
            f"Ориентир: ~{PER_ANSWER_RUB_LOW:g}–{PER_ANSWER_RUB_HIGH:g} ₽ за один ответ "
            f"(умножаем на объём)."
        ),
        "",
        section("Сравнение по объёму", icon="📊"),
        "",
    ]
    for vol in PRESET_VOLUMES:
        lines.append(_volume_overview_line(vol, lite_rub=lite_rub, pro_rub=pro_rub))
    lines.extend(
        [
            "",
            muted("👇 Нажмите объём — детальный расчёт и кнопка оплаты."),
        ]
    )
    return "\n".join(lines)


def build_calculator_detail(pricing: SubscriptionPricing, volume: int) -> str:
    volume = max(1, min(volume, 50_000))
    lite_rub = pricing.lite_rub
    pro_rub = pricing.pro_rub
    low = _pay_per_answer_total(volume, PER_ANSWER_RUB_LOW)
    mid = _pay_per_answer_total(volume, PER_ANSWER_RUB_MID)
    high = _pay_per_answer_total(volume, PER_ANSWER_RUB_HIGH)
    hint = _best_plan_hint(volume, lite_rub=lite_rub, pro_rub=pro_rub)

    lines = [
        brand_title(f"{volume} ответов / мес", tagline="Примерный расчёт", icon="🧮"),
        section("Pay-per-answer", icon="💸"),
        "",
        bullet(f"~{PER_ANSWER_RUB_LOW:g} ₽/шт → <b>{_fmt_rub(low)}</b>"),
        bullet(f"~{PER_ANSWER_RUB_MID:g} ₽/шт → <b>{_fmt_rub(mid)}</b>"),
        bullet(f"~{PER_ANSWER_RUB_HIGH:g} ₽/шт → <b>{_fmt_rub(high)}</b>"),
        section("Голос бренда", icon="✨"),
        "",
        bullet(f"Lite (фикс) → <b>{_fmt_rub(lite_rub)}</b> / мес"),
        bullet(f"PRO (фикс) → <b>{_fmt_rub(pro_rub)}</b> / мес"),
    ]
    if hint:
        lines.extend(["", hint])
    lines.extend(
        [
            "",
            muted("Точные цены — в «Способ оплаты». Калькулятор — ориентир, не оферта."),
        ]
    )
    return "\n".join(lines)
