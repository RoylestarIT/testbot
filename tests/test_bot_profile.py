from app.bot.bot_profile import (
    DEFAULT_SHORT_DESCRIPTION,
    SHORT_DESCRIPTION_MAX,
    resolve_short_description,
    resolve_description,
    default_bot_commands,
)
from app.core.config import Settings


def test_default_short_description_within_limit() -> None:
    assert len(DEFAULT_SHORT_DESCRIPTION) <= SHORT_DESCRIPTION_MAX


def test_resolve_short_description_uses_custom() -> None:
    settings = Settings(
        BOT_TOKEN="x",
        BOT_SHORT_DESCRIPTION="Кастомное описание",
    )
    assert resolve_short_description(settings) == "Кастомное описание"


def test_default_commands_include_start_and_subscription() -> None:
    names = [c.command for c in default_bot_commands()]
    assert "start" in names
    assert "my_subscription" in names
    assert "admin" not in names
