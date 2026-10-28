from app.bot.wb_key_guide import parse_wb_help_context, wb_key_guide_text


def test_parse_wb_help_context() -> None:
    assert parse_wb_help_context("help:wb_key") == ("text", "acc")
    assert parse_wb_help_context("help:wb_key:connect") == ("text", "connect")
    assert parse_wb_help_context("help:wb_key:album:onboard") == ("album", "onboard")


def test_wb_key_guide_lists_seven_steps() -> None:
    text = wb_key_guide_text()
    for n in range(1, 8):
        assert f"{n}." in text
    assert "Вопросы и отзывы" in text
