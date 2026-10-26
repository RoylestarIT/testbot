"""Уведомление о новых отзывах после Sync (ручного или фонового)."""

from __future__ import annotations

from aiogram import Bot
from app.bot.keyboards.empty_states import poller_notify_keyboard
from app.bot.utils.proactive_notify import send_proactive
from app.db.models import Review, ReviewStatus, User
from app.services.marketplace.auto_publish_types import AutoPublishOutcome
from app.services.poller_notify import PollerUserNotify, build_poller_notify_text


def apply_review_to_notify_stats(
    stats: PollerUserNotify,
    review: Review,
    outcome: AutoPublishOutcome,
) -> None:
    if outcome.status == "published":
        stats.auto_published += 1
        if outcome.reply_preview:
            stats.auto_previews.append(outcome.reply_preview)
    if review.status == ReviewStatus.NEW:
        stats.queue_new += 1
        if review.rating is not None and review.rating <= 3:
            stats.queue_negative += 1


async def send_new_reviews_notify_if_needed(
    bot: Bot,
    user: User,
    stats: PollerUserNotify,
) -> None:
    if not user.notify_new_reviews:
        return
    text = build_poller_notify_text(
        stats=stats,
        negative_only=user.notify_negative_only,
    )
    if text is None:
        return
    await send_proactive(bot, user.tg_id, text, reply_markup=poller_notify_keyboard())
