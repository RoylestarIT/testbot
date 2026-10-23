from __future__ import annotations

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.db.models import MarketplaceAccount, Review
from app.db.repositories.reply import ReplyRepository
from app.services.generation_limit import is_pro_user
from app.services.llm import LLMError, generate_replies
from app.services.marketplace.base import MarketplaceAPIError
from app.services.marketplace.product_context import product_context_for_llm
from app.services.marketplace.publish_service import publish_reply_to_marketplace
from app.services.tone_resolver import resolve_tone_input

AUTO_PUBLISH_MIN_RATING = 4


async def try_auto_publish_review(
    session: AsyncSession,
    *,
    account: MarketplaceAccount,
    review: Review,
    settings: Settings | None = None,
) -> bool:
    """PRO + auto_publish: для 4–5★ генерирует один ответ и публикует без подтверждения."""
    if not account.auto_publish_enabled:
        return False
    if not await is_pro_user(session, account.user_id):
        return False
    if review.rating is not None and review.rating < AUTO_PUBLISH_MIN_RATING:
        return False

    settings = settings or get_settings()
    tone = await resolve_tone_input(session, account.user_id, "default")
    try:
        product_context = product_context_for_llm(review.raw_json, account.marketplace)
        variants = await generate_replies(
            review.text or "",
            review.rating or 5,
            tone,
            count=1,
            product_context=product_context,
            settings=settings,
        )
    except LLMError as exc:
        logger.warning("Auto-publish LLM failed review_id={} err={}", review.id, exc)
        return False

    if not variants:
        return False

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
        return False

    logger.info("Auto-published review_id={} account_id={}", review.id, account.id)
    return True
