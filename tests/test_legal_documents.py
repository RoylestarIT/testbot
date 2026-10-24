from app.bot.legal.documents import LegalDocKind, document_page, page_count
from app.core.config import Settings


def _settings(**overrides: str) -> Settings:
    """model_construct — без перезаписи из .env на CI/VM."""
    base = {
        "bot_token": "test:token",
        "legal_operator_name": "ИП Примеров",
        "support_username": "brend_voice_support",
    }
    base.update(overrides)
    return Settings.model_construct(**base)


def test_privacy_pages_within_telegram_limit() -> None:
    settings = _settings()
    total = page_count(LegalDocKind.PRIVACY, settings)
    assert total >= 1
    for i in range(total):
        page = document_page(LegalDocKind.PRIVACY, i, settings)
        assert page is not None
        assert len(page) <= 4096
        assert "Otveto" not in page and "АИ ВЭЙ" not in page
        assert "LEGAL_OPERATOR_NAME" not in page
        assert "Голос бренда" in page


def test_terms_pages_within_telegram_limit() -> None:
    settings = _settings()
    total = page_count(LegalDocKind.TERMS, settings)
    assert total >= 1
    for i in range(total):
        page = document_page(LegalDocKind.TERMS, i, settings)
        assert page is not None
        assert len(page) <= 4096
        assert "Wildberries" in page or "WB" in page


def test_operator_name_injected() -> None:
    settings = _settings(legal_operator_name="ООО «Тест»")
    page = document_page(LegalDocKind.PRIVACY, 0, settings)
    assert page is not None
    assert "ООО «Тест»" in page
