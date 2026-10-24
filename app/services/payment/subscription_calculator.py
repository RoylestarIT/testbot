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


def _market_mid_total(volume: int) -> int:
    return _pay_per_answer_total(volume, PER_ANSWER_RUB_MID)


def _motivation_lines(volume: int, *, lite_rub: int, pro_rub: int) -> list[str]:
    """Мягкие аргументы при выгодной подписке — без агрессивных сравнений."""
    mid = _market_mid_total(volume)
    lines: list[str] = []

    if mid <= lite_rub:
        lines.extend(
            [
                section("Если объём небольшой", icon="💡"),
                "",
                bullet(
                    "Оплата «за ответ» на рынке иногда выходит дешевле — "
                    "мы не скрываем цифры."
                ),
                bullet(
                    "Фикс всё равно удобен, когда ответов станет больше: "
                    "бюджет известен заранее, без сюрпризов в конце месяца."
                ),
                bullet(muted("📱 Весь цикл в Telegram — sync, 3 варианта, вы решаете финальный текст.")),
            ]
        )
        return lines

    save_lite = mid - lite_rub
    save_pro = mid - pro_rub
    lines.extend(
        [
            section("Почему здесь смотреть на подписку", icon="💡"),
            "",
            bullet(
                f"При ~{volume} отв./мес и ~{PER_ANSWER_RUB_MID:g} ₽/ответ на рынке "
                f"выходит ~<b>{_fmt_rub(mid)}</b> — ✨ Lite <b>{_fmt_rub(lite_rub)}</b> "
                f"(ориентир экономии ~<b>{_fmt_rub(save_lite)}</b>)."
            ),
        ]
    )
    if save_pro > 0 and volume >= 300:
        lines.append(
            bullet(
                f"🚀 PRO <b>{_fmt_rub(pro_rub)}</b> — если нужен publish в WB/Ozon и авто 4–5★; "
                f"на этом объёме тоже ниже типичного «за ответ» (~{_fmt_rub(save_pro)})."
            )
        )
    lines.extend(
        [
            "",
            muted("Плюс к цене — без отдельного кабинета:"),
            bullet("⏱ Ответы из Telegram, не «весь день в маркетплейсе»"),
            bullet("✋ Негатив 1–3★ не уходит в автомат — только вы"),
            bullet("🎨 Три варианта текста и правка перед отправкой"),
        ]
    )
    if volume >= 500:
        lines.append(bullet("📈 На растущем объёме фикс не «раздувается» с каждым новым отзывом"))
    return lines


def _best_plan_hint(volume: int, *, lite_rub: int, pro_rub: int) -> str:
    mid_market = _market_mid_total(volume)
    if mid_market <= lite_rub:
        return muted("Честно: на этом объёме pay-per-answer может быть ниже — см. блок выше.")
    if pro_rub < mid_market and volume >= 400:
        return muted(f"Подсказка: при {volume} отв./мес чаще смотрят на 🚀 PRO (publish + авто).")
    return muted(f"Подсказка: ✨ Lite уже выгоднее ~{PER_ANSWER_RUB_MID:g} ₽/ответ на этом объёме.")


def _volume_overview_line(vol: int, *, lite_rub: int, pro_rub: int) -> str:
    low = _pay_per_answer_total(vol, PER_ANSWER_RUB_LOW)
    high = _pay_per_answer_total(vol, PER_ANSWER_RUB_HIGH)
    mid = _pay_per_answer_total(vol, PER_ANSWER_RUB_MID)
    hint = ""
    if mid > lite_rub:
        save = mid - lite_rub
        hint = f" → ✨ Lite (~−{_fmt_rub(save)} vs 2₽/отв.)"
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
    motivation = _motivation_lines(volume, lite_rub=lite_rub, pro_rub=pro_rub)

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
        "",
    ]
    lines.extend(motivation)
    if hint:
        lines.extend(["", hint])
    lines.extend(
        [
            "",
            muted("Точные цены — в «Способ оплаты». Калькулятор — ориентир, не оферта."),
        ]
    )
    return "\n".join(lines)
