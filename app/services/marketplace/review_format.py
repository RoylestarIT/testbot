from __future__ import annotations

from typing import Any

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
            return f"артикул WB {nm}"
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
    rating = review.rating if review.rating is not None else "?"
    stars_line = f"⭐ Оценка: <b>{rating}/5</b>"
    if isinstance(review.rating, int) and review.rating <= 3:
        stars_line += "\n⚠️ <i>Негативный отзыв — ответьте особенно внимательно.</i>"
    shop = account.shop_name if account and account.shop_name else mp
    product = _product_hint(review.raw_json, marketplace)
    product_line = f"\n🛍 {product}" if product else ""
    text = (review.text or "—").strip()
    if len(text) > 800:
        text = text[:800] + "…"
    if can_publish_via_api:
        publish_line = "📌 Отправка в маркетплейс из бота: <b>доступна</b> (PRO / trial / квота)\n"
    else:
        publish_line = (
            "📌 Отправка в API: <b>нужен PRO</b> · сейчас — «Скопировать ответ»\n"
        )
    return (
        f"📄 <b>Отзыв</b> · {shop}\n"
        f"{stars_line}{product_line}\n"
        f"Площадка: {mp}\n"
        f"{publish_line}\n"
        f"{text}\n\n"
        "Выберите <b>тон ответа</b> (или быстрый пресет ниже):"
    )
