from app.db.models import Marketplace
from app.services.marketplace.product_context import product_context_for_llm, product_hint_short


def test_product_context_wb_from_raw_json() -> None:
    raw = {
        "productName": "Кружка керамическая",
        "nmId": 123456,
        "brandName": "HomeBrand",
    }
    ctx = product_context_for_llm(raw, Marketplace.WB)
    assert ctx is not None
    assert "Кружка" in ctx
    assert "123456" in ctx
    assert "HomeBrand" in ctx


def test_product_context_ozon_sku_and_name() -> None:
    raw = {"sku": 987, "product_name": "Наушники TWS"}
    ctx = product_context_for_llm(raw, Marketplace.OZON)
    assert ctx is not None
    assert "987" in ctx
    assert "Наушники" in ctx


def test_product_context_manual_review_returns_none() -> None:
    assert product_context_for_llm({"source": "manual"}, Marketplace.WB) is None


def test_product_hint_short_truncates_long_context() -> None:
    long_name = "A" * 200
    raw = {"productName": long_name}
    hint = product_hint_short(raw, Marketplace.WB)
    assert hint is not None
    assert len(hint) <= 120
    assert hint.endswith("…")
