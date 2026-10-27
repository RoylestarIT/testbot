from app.bot.product_news import build_release_history_text
from app.bot.user_errors import user_error_from_exception
from app.core.security import EncryptionError
from app.services.reply_feedback import should_ask_feedback


def test_release_history_contains_versions() -> None:
    text = build_release_history_text()
    assert "2025-10-v1" in text
    assert "2025-10-v2" in text


def test_user_error_encryption() -> None:
    err = user_error_from_exception(EncryptionError("x"))
    assert "ключ кабинета" in err.html
    assert err.reply_markup is not None


def test_feedback_every_fifth_action() -> None:
    assert not should_ask_feedback(4)
    assert should_ask_feedback(5)
    assert should_ask_feedback(10)
