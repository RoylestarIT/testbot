from app.bot.product_news import build_product_news_banner, user_should_see_product_news
from app.core.config import Settings
from app.db.models import User


def test_product_news_shown_until_dismissed() -> None:
    settings = Settings.model_construct(bot_token="x", product_news_version="2025-10-v1")
    user = User(id=1, tg_id=1, product_news_seen_version="")
    assert user_should_see_product_news(user, settings) is True
    user.product_news_seen_version = "2025-10-v1"
    assert user_should_see_product_news(user, settings) is False


def test_product_news_banner_mentions_legal() -> None:
    settings = Settings.model_construct(bot_token="x", product_news_version="v1")
    text = build_product_news_banner(settings)
    assert "/legal" in text
