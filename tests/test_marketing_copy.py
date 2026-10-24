from app.bot.marketing import for_whom_text, market_compare_text, why_us_hub_text


def test_why_us_hub_mentions_time_and_salary_savings() -> None:
    text = why_us_hub_text()
    assert len(text) <= 4096
    assert "время" in text.lower() or "⏱" in text
    assert "30" in text or "сотрудник" in text.lower()
    assert "800" in text
    assert "лояль" in text.lower() or "❤️" in text


def test_for_whom_structured_for_sellers() -> None:
    text = for_whom_text()
    assert len(text) <= 4096
    assert "селлер" in text.lower()
    assert "───────────────" in text
    assert "получите" in text.lower()
