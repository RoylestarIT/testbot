from __future__ import annotations

import csv
import io
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Marketplace, Review, ReviewStatus
from app.db.repositories.reply import ReplyRepository
from app.db.repositories.review import ReviewRepository


def _fmt_dt(when: datetime | None) -> str:
    if when is None:
        return ""
    if when.tzinfo is None:
        return when.isoformat()
    return when.astimezone().isoformat()


async def build_history_csv(session: AsyncSession, user_id: int, *, limit: int = 2000) -> bytes:
    reviews = await ReviewRepository(session).list_for_export(user_id, limit=limit)
    reply_map = await ReplyRepository(session).latest_text_by_review_ids([r.id for r in reviews])

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(
        [
            "created_at",
            "marketplace",
            "shop",
            "rating",
            "status",
            "review_text",
            "reply_text",
            "external_id",
        ]
    )
    for review in reviews:
        acc = review.account
        mp = acc.marketplace.value if acc else ""
        shop = acc.shop_name or "" if acc else ""
        writer.writerow(
            [
                _fmt_dt(review.created_at),
                mp,
                shop,
                review.rating if review.rating is not None else "",
                review.status.value,
                (review.text or "").replace("\n", " ").strip(),
                (reply_map.get(review.id) or "").replace("\n", " ").strip(),
                review.external_id,
            ]
        )
    payload = buf.getvalue().encode("utf-8-sig")
    return payload
