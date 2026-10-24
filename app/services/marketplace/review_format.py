from __future__ import annotations

from app.bot.ui import REVIEW_CARD_STEPS, muted, quote, review_stars
from app.db.models import Marketplace, MarketplaceAccount, Review
from app.services.marketplace.product_context import product_hint_short


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
    product = product_hint_short(review.raw_json, marketplace)

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
    lines.append(muted(REVIEW_CARD_STEPS))
    lines.append(muted("Выберите тон или ⚡ шаблон:"))
    if isinstance(rating, int) and rating <= 3:
        lines.insert(2, "⚠️ Низкая оценка — проверьте ответ перед отправкой")
    return "\n".join(lines)
