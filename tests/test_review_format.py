from app.db.models import Marketplace, MarketplaceAccount, Review, ReviewStatus
from app.services.marketplace.review_format import format_review_card


def test_review_card_shows_pro_badge_when_no_api_publish() -> None:
    review = Review(
        id=1,
        account_id=1,
        external_id="x",
        rating=5,
        text="Отличный товар",
        status=ReviewStatus.NEW,
    )
    account = MarketplaceAccount(
        id=1,
        user_id=1,
        marketplace=Marketplace.WB,
        encrypted_api_key="x",
        shop_name="Test",
        is_active=True,
    )
    body = format_review_card(review, account, can_publish_via_api=False)
    assert "Скопировать" in body or "Lite" in body


def test_review_card_shows_publish_available() -> None:
    review = Review(
        id=1,
        account_id=1,
        external_id="x",
        rating=5,
        text="Ok",
        status=ReviewStatus.NEW,
    )
    account = MarketplaceAccount(
        id=1,
        user_id=1,
        marketplace=Marketplace.OZON,
        encrypted_api_key="x",
        is_active=True,
    )
    body = format_review_card(review, account, can_publish_via_api=True)
    assert "publish" in body.lower()
