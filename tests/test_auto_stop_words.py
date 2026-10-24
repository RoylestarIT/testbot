from app.services.auto_stop_words import parse_stop_words, review_matches_stop_words


def test_parse_stop_words_splits_and_lowercases() -> None:
    assert parse_stop_words("Брак, возврат\nDEFECT") == ["брак", "возврат", "defect"]


def test_review_matches_stop_words_substring() -> None:
    assert review_matches_stop_words("Товар с браком", "брак")
    assert not review_matches_stop_words("Отлично", "брак")
    assert not review_matches_stop_words("ok", None)
