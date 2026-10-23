from __future__ import annotations

from typing import Any

from app.bot.ui import DIVIDER, muted, quote, review_stars, section
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
        mp = "Wildberries" if account.marketplace == Marketplace.WB else "Ozon"
    rating = review.rating if review.rating is not None else 0
    shop = account.shop_name if account and account.shop_name else mp
    product = _product_hint(review.raw_json, marketplace)

    stars = review_stars(rating if isinstance(rating, int) else 0)
    rating_line = f"{stars}  <b>{rating}/5</b>" if isinstance(review.rating, int) else muted("Без оценки")

    if can_publish_via_api:
        channel = "PRO · publish из бота доступен"
    else:
        channel = "Lite · ответ через «Скопировать»"

    text = (review.text or "—").strip()
    if len(text) > 800:
        text = text[:800] + "…"

    lines = [
        f"✦ <b>Отзыв</b>  ·  {shop}",
        DIVIDER,
        section("Оценка"),
        f"  {rating_line}",
    ]
    if isinstance(review.rating, int) and review.rating <= 3:
        lines.append(f"  {muted('Негатив — ответьте внимательно')}")
    lines.append(section("Товар"))
    lines.append(f"  {product or muted('—')}")
    lines.append(section("Канал"))
    lines.append(f"  {channel}")
    lines.append(section("Текст покупателя"))
    lines.append(quote(text))
    lines.append("")
    lines.append(muted("Выберите тон ответа или ⚡ быстрый шаблон:"))
    return "\n".join(lines)
