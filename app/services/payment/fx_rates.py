from __future__ import annotations

from dataclasses import dataclass

from app.core.config import Settings, get_settings


@dataclass(frozen=True)
class SubscriptionPricing:
    lite_rub: int
    pro_rub: int
    lite_byn: float
    pro_byn: float
    source: str = "фиксированный прайс"

    def _plan_rub_byn(self, *, lite: bool) -> str:
        if lite:
            return f"{_fmt_rub(self.lite_rub)} / {self.lite_byn:g} BYN"
        return f"{_fmt_rub(self.pro_rub)} / {self.pro_byn:g} BYN"

    def lite_line(self) -> str:
        return f"✨ Lite — {self._plan_rub_byn(lite=True)}"

    def pro_line(self) -> str:
        return f"💎 PRO — {self._plan_rub_byn(lite=False)}"

    def lite_button(self) -> str:
        return f"✨ Lite · {_fmt_rub(self.lite_rub)}"

    def pro_button(self) -> str:
        return f"💎 PRO · {_fmt_rub(self.pro_rub)}"

    def crypto_lite_button(self) -> str:
        return f"🪙 Lite · {_fmt_rub(self.lite_rub)}"

    def crypto_pro_button(self) -> str:
        return f"🪙 PRO · {_fmt_rub(self.pro_rub)}"

    def lite_price_label(self) -> str:
        return self._plan_rub_byn(lite=True)

    def pro_price_label(self) -> str:
        return self._plan_rub_byn(lite=False)


def _fmt_rub(amount: int) -> str:
    return f"{amount:,}".replace(",", " ") + " ₽"


async def get_subscription_pricing(settings: Settings | None = None) -> SubscriptionPricing:
    settings = settings or get_settings()
    return SubscriptionPricing(
        lite_rub=settings.subscription_lite_price_rub,
        pro_rub=settings.subscription_pro_price_rub,
        lite_byn=settings.subscription_lite_price_byn,
        pro_byn=settings.subscription_pro_price_byn,
    )
