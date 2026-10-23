from __future__ import annotations

import time
from dataclasses import dataclass

from app.core.config import Settings, get_settings
from app.services.payment.crypto_pay import CryptoPayError, _api_request, crypto_pay_enabled

_CACHE_TTL_SEC = 1800
_cache: tuple[float, float, float] | None = None  # (ts, rub_per_usd, byn_per_usd)


@dataclass(frozen=True)
class SubscriptionPricing:
    lite_usd: float
    pro_usd: float
    rub_per_usd: float
    byn_per_usd: float
    source: str

    def rub_for(self, usd: float) -> int:
        return int(round(usd * self.rub_per_usd))

    def byn_for(self, usd: float) -> float:
        return round(usd * self.byn_per_usd, 2)

    def format_usd_line(self, usd: float) -> str:
        rub = self.rub_for(usd)
        byn = self.byn_for(usd)
        return f"${usd:g} ≈ {_fmt_rub(rub)} / {byn:g} BYN"

    def lite_line(self) -> str:
        return f"✨ Lite — {self.format_usd_line(self.lite_usd)}"

    def pro_line(self) -> str:
        return f"💎 PRO — {self.format_usd_line(self.pro_usd)}"

    def lite_button(self) -> str:
        return f"✨ Lite · {self.format_usd_line(self.lite_usd)}"

    def pro_button(self) -> str:
        return f"💎 PRO · {self.format_usd_line(self.pro_usd)}"

    def crypto_lite_button(self) -> str:
        return f"🪙 Lite · {self.format_usd_line(self.lite_usd)}"

    def crypto_pro_button(self) -> str:
        return f"🪙 PRO · {self.format_usd_line(self.pro_usd)}"


def _fmt_rub(amount: int) -> str:
    return f"{amount:,}".replace(",", " ") + " ₽"


def _parse_usd(value: str, default: float) -> float:
    try:
        return float(value.replace(",", "."))
    except ValueError:
        return default


async def _fetch_crypto_rates(settings: Settings) -> tuple[float, float] | None:
    if not crypto_pay_enabled(settings):
        return None
    try:
        result = await _api_request(settings, "getExchangeRates")
    except CryptoPayError:
        return None
    items = result if isinstance(result, list) else []
    rub_rate: float | None = None
    byn_rate: float | None = None
    for item in items:
        if not isinstance(item, dict) or not item.get("is_valid", True):
            continue
        if item.get("source") != "USDT":
            continue
        target = item.get("target")
        try:
            rate = float(item.get("rate", 0))
        except (TypeError, ValueError):
            continue
        if rate <= 0:
            continue
        if target == "RUB":
            rub_rate = rate
        elif target == "BYN":
            byn_rate = rate
    if rub_rate is None or byn_rate is None:
        return None
    return rub_rate, byn_rate


async def get_subscription_pricing(settings: Settings | None = None) -> SubscriptionPricing:
    global _cache
    settings = settings or get_settings()
    lite = _parse_usd(settings.crypto_lite_amount_usd, 10.0)
    pro = _parse_usd(settings.crypto_pro_amount_usd, 20.0)
    pro = _parse_usd(settings.subscription_pro_usd_label, pro)
    lite = _parse_usd(settings.subscription_lite_usd_label, lite)

    now = time.time()
    rub_per_usd = settings.fx_fallback_usd_rub
    byn_per_usd = settings.fx_fallback_usd_byn
    source = "ориентир из настроек"

    if _cache and now - _cache[0] < _CACHE_TTL_SEC:
        _, rub_per_usd, byn_per_usd = _cache
        source = "Crypto Bot · курс"
    else:
        live = await _fetch_crypto_rates(settings)
        if live is not None:
            rub_per_usd, byn_per_usd = live
            source = "Crypto Bot · курс"
            _cache = (now, rub_per_usd, byn_per_usd)

    return SubscriptionPricing(
        lite_usd=lite,
        pro_usd=pro,
        rub_per_usd=rub_per_usd,
        byn_per_usd=byn_per_usd,
        source=source,
    )
