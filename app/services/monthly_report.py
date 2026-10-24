from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.ui import brand_title, muted
from app.services.period_analytics import (
    build_period_analytics_block,
    count_closed_with_activity_in_period,
    count_distinct_reviews_with_generation,
    median_hours_to_first_reply,
)


async def build_monthly_report_text(session: AsyncSession, user_id: int) -> str:
    w30_gen = await count_distinct_reviews_with_generation(session, user_id, days=30)
    w30_closed = await count_closed_with_activity_in_period(session, user_id, days=30)
    median_h = await median_hours_to_first_reply(session, user_id, days=30)
    analytics = await build_period_analytics_block(session, user_id)

    lines = [
        brand_title("Отчёт за 30 дней", tagline="Сводка для селлера", icon="📆"),
        "",
        f"· Генерации по <b>{w30_gen}</b> отзывам",
        f"· Закрыто (ответ дан): <b>{w30_closed}</b>",
    ]
    if median_h is not None:
        lines.append(f"· Медиана до 1-го ответа: <b>{median_h:g}</b> ч")
    lines.extend(["", analytics, "", muted("Полный CSV: 📚 История → экспорт в боте.")])
    return "\n".join(lines)
