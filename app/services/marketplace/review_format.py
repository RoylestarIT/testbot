from __future__ import annotations

from app.db.models import Marketplace, MarketplaceAccount, Review


def format_review_card(review: Review, account: MarketplaceAccount | None) -> str:
    mp = "—"
    if account is not None:
        mp = "Wildberries" if account.marketplace == Marketplace.WB else "Ozon"
    rating = review.rating if review.rating is not None else "?"
    stars_line = f"Оценка: <b>{rating}/5</b>"
    if isinstance(review.rating, int) and review.rating <= 3:
        stars_line += " ⚠️ <i>негатив — проверьте ответ вручную</i>"
    shop = account.shop_name if account and account.shop_name else mp
    text = (review.text or "—").strip()
    if len(text) > 800:
        text = text[:800] + "…"
    return (
        f"<b>Отзыв</b> ({shop})\n"
        f"{stars_line}\n"
        f"Площадка: {mp}\n\n"
        f"{text}\n\n"
        "Выберите <b>тон ответа</b>:"
    )
