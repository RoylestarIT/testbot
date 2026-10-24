from __future__ import annotations

from app.bot.ui import bullet, muted
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


def _calc_title(screen: str, tagline: str) -> str:
    return f"🧮 <b>{screen}</b>\n{muted(tagline)}"


def _calc_section(icon: str, title: str) -> str:
    return f"{icon} <b>{title}</b>"


def _lines(*parts: str) -> str:
    return "\n".join(p for p in parts if p)


def _motivation_block(volume: int, *, lite_rub: int, pro_rub: int) -> str:
    """Компактный блок мотивации — без лишних пустых строк."""
    mid = _market_mid_total(volume)

    if mid <= lite_rub:
        return _lines(
            _calc_section("💡", "Небольшой объём"),
            bullet(
                "Pay-per-answer может быть дешевле — цифры выше честные. "
                "Фикс удобен, когда ответов больше: бюджет известен заранее."
            ),
            bullet("📱 Telegram: sync → 3 варианта → вы выбираете текст."),
        )

    save_lite = mid - lite_rub
    save_pro = mid - pro_rub
    head = bullet(
        f"~{PER_ANSWER_RUB_MID:g} ₽/ответ → ~{_fmt_rub(mid)} · "
        f"✨ Lite {_fmt_rub(lite_rub)} "
        f"(~−{_fmt_rub(save_lite)} vs рынок)"
    )
    pro_line = ""
    if save_pro > 0 and volume >= 300:
        pro_line = bullet(
            f"🚀 PRO {_fmt_rub(pro_rub)} — publish + авто 4–5★ "
            f"(~−{_fmt_rub(save_pro)} vs рынок на этом объёме)"
        )
    extras = bullet(
        "⏱ В Telegram · ✋ негатив только вы · 🎨 правка перед отправкой"
    )
    growth = ""
    if volume >= 500:
        growth = bullet("📈 Фикс не растёт с каждым новым отзывом")
    return _lines(_calc_section("💡", "Почему подписка"), head, pro_line, extras, growth)


def _volume_overview_line(vol: int, *, lite_rub: int, pro_rub: int) -> str:
    low = _pay_per_answer_total(vol, PER_ANSWER_RUB_LOW)
    high = _pay_per_answer_total(vol, PER_ANSWER_RUB_HIGH)
    mid = _pay_per_answer_total(vol, PER_ANSWER_RUB_MID)
    hint = ""
    if mid > lite_rub:
        save = mid - lite_rub
        hint = f" → ✨ Lite (−{_fmt_rub(save)})"
    elif mid > pro_rub:
        hint = " → 🚀 PRO"
    return bullet(f"<b>{vol}</b> отв/мес · {_fmt_rub(low)}–{_fmt_rub(high)}{hint}")


def build_calculator_table(pricing: SubscriptionPricing) -> str:
    lite_rub = pricing.lite_rub
    pro_rub = pricing.pro_rub
    from app.bot.subscription_ui import SUBSCRIPTION_SEP

    volumes = "\n".join(
        _volume_overview_line(vol, lite_rub=lite_rub, pro_rub=pro_rub) for vol in PRESET_VOLUMES
    )
    return _lines(
        _calc_title("Калькулятор", "Подписка vs ₽ за ответ"),
        SUBSCRIPTION_SEP,
        _calc_section("💎", "Фикс / мес"),
        bullet(f"Lite — <b>{_fmt_rub(lite_rub)}</b>"),
        bullet(f"PRO — <b>{_fmt_rub(pro_rub)}</b>"),
        _calc_section("💸", "Рынок pay-per-answer"),
        muted(f"~{PER_ANSWER_RUB_LOW:g}–{PER_ANSWER_RUB_HIGH:g} ₽/ответ × объём"),
        _calc_section("📊", "Объёмы"),
        volumes,
        muted("👇 Нажмите объём — детали и оплата"),
    )


def build_calculator_detail(pricing: SubscriptionPricing, volume: int) -> str:
    volume = max(1, min(volume, 50_000))
    lite_rub = pricing.lite_rub
    pro_rub = pricing.pro_rub
    low = _pay_per_answer_total(volume, PER_ANSWER_RUB_LOW)
    mid = _pay_per_answer_total(volume, PER_ANSWER_RUB_MID)
    high = _pay_per_answer_total(volume, PER_ANSWER_RUB_HIGH)
    mid_market = _market_mid_total(volume)
    plan_hint = ""
    if mid_market > pro_rub and volume >= 400:
        plan_hint = muted(f"Чаще смотрят 🚀 PRO при {volume} отв/мес")
    elif mid_market > lite_rub:
        plan_hint = muted(f"✨ Lite выгоднее ~{PER_ANSWER_RUB_MID:g} ₽/ответ здесь")

    return _lines(
        _calc_title(f"{volume} ответов / мес", "Примерный расчёт"),
        _calc_section("💸", "Pay-per-answer"),
        bullet(f"1 ₽ → {_fmt_rub(low)} · 2 ₽ → {_fmt_rub(mid)} · 3 ₽ → {_fmt_rub(high)}"),
        _calc_section("✨", "Голос бренда"),
        bullet(f"Lite <b>{_fmt_rub(lite_rub)}</b>/мес · PRO <b>{_fmt_rub(pro_rub)}</b>/мес"),
        _motivation_block(volume, lite_rub=lite_rub, pro_rub=pro_rub),
        plan_hint,
        muted("Цены в «Оплатить». Калькулятор — ориентир."),
    )
