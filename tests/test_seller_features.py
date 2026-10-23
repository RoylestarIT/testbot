from app.db.models import Review, ReviewStatus
from app.services.bulk_quick_reply import is_bulk_eligible
from app.services.reply_templates import add_template, list_templates, remove_template


class _User:
    reply_templates = None


def test_bulk_eligible_short_high_rating() -> None:
    review = Review(id=1, account_id=1, external_id="a", rating=5, text="👍", status=ReviewStatus.NEW)
    assert is_bulk_eligible(review) is True


def test_bulk_not_eligible_low_rating() -> None:
    review = Review(id=1, account_id=1, external_id="a", rating=3, text="", status=ReviewStatus.NEW)
    assert is_bulk_eligible(review) is False


def test_reply_templates_crud() -> None:
    user = _User()
    ok, err = add_template(user, label="Спасибо", text="Благодарим за отзыв!")
    assert ok and err is None
    assert len(list_templates(user)) == 1
    tpl_id = list_templates(user)[0]["id"]
    assert remove_template(user, tpl_id) is True
    assert list_templates(user) == []
