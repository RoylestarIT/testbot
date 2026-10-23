from app.services.marketplace.ozon import _parse_ozon_review
from app.services.marketplace.wildberries import _parse_wb_feedback


def test_parse_wb_feedback_merges_text_parts() -> None:
    dto = _parse_wb_feedback(
        {
            "id": "abc-123",
            "text": "Норм товар",
            "pros": "Быстрая доставка",
            "cons": "",
            "productValuation": 5,
            "userName": "Покупатель",
            "createdDate": "2024-01-15T10:00:00Z",
        }
    )
    assert dto.external_id == "abc-123"
    assert dto.rating == 5
    assert "Норм товар" in (dto.text or "")
    assert "Быстрая доставка" in (dto.text or "")
    assert dto.author == "Покупатель"
    assert dto.created_at is not None


def test_parse_ozon_review_basic() -> None:
    dto = _parse_ozon_review(
        {
            "id": 999,
            "rating": 4,
            "text": "Хорошо",
            "published_at": "2024-02-01T12:00:00Z",
            "status": "UNPROCESSED",
        }
    )
    assert dto.external_id == "999"
    assert dto.rating == 4
    assert dto.text == "Хорошо"
    assert dto.created_at is not None
