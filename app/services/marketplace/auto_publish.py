from __future__ import annotations

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.db.models import MarketplaceAccount, Review
from app.db.repositories.reply import ReplyRepository
from app.services.generation_limit import is_pro_user
from app.services.llm import LLMError, generate_replies
from app.services.marketplace.base import MarketplaceAPIError
from app.services.marketplace.auto_publish_types import AutoPublishOutcome
from app.services.marketplace.product_context import product_context_for_llm
from app.services.marketplace.publish_service import publish_reply_to_marketplace
from app.services.auto_stop_words import review_matches_stop_words
from app.services.tone_resolver import resolve_tone_input
from app.db.repositories.user import UserRepository

DEFAULT_AUTO_PUBLISH_MIN_RATING = 4


def _review_has_text(review: Review) -> bool:
    return bool((review.text or "").strip())


async def try_auto_publish_review(
    session: AsyncSession,
    *,
    account: MarketplaceAccount,
    review: Review,
    settings: Settings | None = None,
) -> AutoPublishOutcome:
    """PRO + auto_publish: для 4–5★ генерирует один ответ и публикует без подтверждения."""
    if not account.auto_publish_enabled:
        return AutoPublishOutcome("skipped")
    if not await is_pro_user(session, account.user_id):
        return AutoPublishOutcome("skipped")
    min_rating = account.auto_publish_min_rating or DEFAULT_AUTO_PUBLISH_MIN_RATING
    if review.rating is not None and review.rating < min_rating:
        return AutoPublishOutcome("skipped")
    if account.auto_publish_stars_only and _review_has_text(review):
        return AutoPublishOutcome("skipped")
    if review_matches_stop_words(review.text, account.auto_publish_stop_words):
        return AutoPublishOutcome("skipped")

    settings = settings or get_settings()
    tone = await resolve_tone_input(session, account.user_id, "default")
    user = await UserRepository(session).get_by_id(account.user_id)
    soft_rec = bool(user and user.soft_product_recommend)
    try:
        product_context = product_context_for_llm(review.raw_json, account.marketplace)
        variants = await generate_replies(
            review.text or "",
            review.rating or 5,
            tone,
            count=1,
            product_context=product_context,
            soft_product_recommend=soft_rec,
            settings=settings,
        )
    except LLMError as exc:
        logger.warning("Auto-publish LLM failed review_id={} err={}", review.id, exc)
        return AutoPublishOutcome("llm_failed")

    if not variants:
        return AutoPublishOutcome("llm_failed")

    text = variants[0]
    await ReplyRepository(session).create(
        review_id=review.id,
        variant_index=0,
        text=text,
        model=settings.openai_model,
    )
    await session.flush()

    try:
        await publish_reply_to_marketplace(session, review, text)
    except MarketplaceAPIError as exc:
        logger.warning("Auto-publish API failed review_id={} err={}", review.id, exc)
        return AutoPublishOutcome("api_failed")

    logger.info("Auto-published review_id={} account_id={}", review.id, account.id)
    preview = text.strip()
    if len(preview) > 120:
        preview = preview[:117] + "…"
    return AutoPublishOutcome("published", reply_preview=preview)
