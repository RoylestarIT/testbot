from __future__ import annotations

from app.bot.ui import brand_title, bullet, muted, section
from app.services.payment.fx_rates import SubscriptionPricing, _fmt_rub

# Типичный рынок «оплата за ответ» (без имён сервисов)
PER_ANSWER_RUB_LOW = 1.0
PER_ANSWER_RUB_MID = 2.0
PER_ANSWER_RUB_HIGH = 3.0

PRESET_VOLUMES = (100, 200, 300, 500, 800, 1000)


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


def build_calculator_table(pricing: SubscriptionPricing) -> str:
    lite_rub = pricing.rub_for(pricing.lite_usd)
    pro_rub = pricing.rub_for(pricing.pro_usd)
    from app.bot.subscription_ui import SUBSCRIPTION_SEP

    lines = [
        brand_title("Калькулятор", tagline="Подписка vs ₽ за ответ", icon="🧮").strip(),
        SUBSCRIPTION_SEP,
        muted(
            f"Рынок ~{PER_ANSWER_RUB_LOW:g}–{PER_ANSWER_RUB_HIGH:g} ₽/ответ · "
            f"Lite {_fmt_rub(lite_rub)} · PRO {_fmt_rub(pro_rub)} / мес"
        ),
        "",
        "<pre>",
        " ответов │  ~1₽/шт │  ~2₽/шт │  ~3₽/шт │  Lite  │  PRO",
        "─────────┼─────────┼─────────┼─────────┼────────┼──────",
    ]
    for vol in PRESET_VOLUMES:
        p1 = _pay_per_answer_total(vol, PER_ANSWER_RUB_LOW)
        p2 = _pay_per_answer_total(vol, PER_ANSWER_RUB_MID)
        p3 = _pay_per_answer_total(vol, PER_ANSWER_RUB_HIGH)
        lines.append(
            f" {vol:>7} │ {p1:>6} ₽ │ {p2:>6} ₽ │ {p3:>6} ₽ │ {lite_rub:>5} │ {pro_rub:>4}"
        )
    lines.append("</pre>")
    lines.append("")
    lines.append(muted("👇 Выберите объём ответов в месяц."))
    return "\n".join(lines)


def build_calculator_detail(pricing: SubscriptionPricing, volume: int) -> str:
    volume = max(1, min(volume, 50_000))
    lite_rub = pricing.rub_for(pricing.lite_usd)
    pro_rub = pricing.rub_for(pricing.pro_usd)
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
