from app.bot.wb_key_guide import parse_wb_help_context, wb_key_guide_text


def test_parse_wb_help_context() -> None:
    assert parse_wb_help_context("help:wb_key") == "acc"
    assert parse_wb_help_context("help:wb_key:connect") == "connect"
    assert parse_wb_help_context("help:wb_key:onboard") == "onboard"


def test_wb_key_guide_lists_seven_steps() -> None:
    text = wb_key_guide_text()
    for n in range(1, 8):
        assert f"{n}." in text
    assert "Вопросы и отзывы" in text
    assert "ИП" not in text
