from __future__ import annotations

from typing import Any

from app.bot.ui import muted, quote, review_stars
from app.db.models import Marketplace, MarketplaceAccount, Review


def _product_hint(raw: dict[str, Any] | None, marketplace: Marketplace | None) -> str | None:
    if not raw:
        return None
    if marketplace == Marketplace.WB:
        name = raw.get("productName") or raw.get("productDetails", {}).get("productName")
        if isinstance(name, str) and name.strip():
            return name.strip()[:120]
        nm = raw.get("nmId") or raw.get("productDetails", {}).get("nmId")
        if nm is not None:
            return f"артикул {nm}"
    if marketplace == Marketplace.OZON:
        sku = raw.get("sku")
        if sku is not None:
            return f"SKU {sku}"
    return None


def format_review_card(
    review: Review,
    account: MarketplaceAccount | None,
    *,
    can_publish_via_api: bool = False,
) -> str:
    mp = "—"
    marketplace = account.marketplace if account else None
    if account is not None:
        mp = "🟣 WB" if account.marketplace == Marketplace.WB else "🔵 Ozon"
    rating = review.rating if review.rating is not None else None
    shop = account.shop_name if account and account.shop_name else mp
    product = _product_hint(review.raw_json, marketplace)

    if isinstance(rating, int):
        stars = review_stars(rating)
        head = f"<b>{shop}</b>  ·  {stars}  ({rating}/5)"
    else:
        head = f"<b>{shop}</b>"

    publish = (
        "🚀 можно отправить из бота"
        if can_publish_via_api
        else "📋 скопируйте ответ в кабинет"
    )

    text = (review.text or "—").strip()
    if len(text) > 700:
        text = text[:700] + "…"

    lines = [
        head,
        muted(f"{mp} · {publish}"),
    ]
    if product:
        lines.append(muted(product))
    lines.append("")
    lines.append(quote(text))
    lines.append("")
    lines.append(muted("Выберите тон или ⚡ шаблон:"))
    if isinstance(rating, int) and rating <= 3:
        lines.insert(2, "⚠️ Низкая оценка — проверьте ответ перед отправкой")
    return "\n".join(lines)
