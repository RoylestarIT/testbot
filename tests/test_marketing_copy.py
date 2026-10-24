from app.bot.marketing import feature_roadmap_text, market_compare_text


def test_market_compare_no_competitor_names() -> None:
    text = market_compare_text()
    assert "Otveto" not in text
    assert "Spix" not in text
    assert "Сравнение с рынком" in text
    assert "Telegram" in text


def test_feature_roadmap_sections() -> None:
    text = feature_roadmap_text()
    assert "Уже есть" in text
    assert "Скоро" in text
    assert "Не в фокусе" in text
    assert "ROADMAP.md" in text
