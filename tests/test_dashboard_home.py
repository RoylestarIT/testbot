from app.bot.ui import dashboard_home


def test_dashboard_home_has_separators_and_no_duplicate_sections() -> None:
    text = dashboard_home(
        status_block="<blockquote>📬 test</blockquote>",
        meta_lines=["🆓 Free", "🏪 shop"],
        nudge=None,
        footer="sync ok",
    )
    assert "Голос бренда" in text
    assert text.count("───────────────") == 2
    assert "Почему" not in text
