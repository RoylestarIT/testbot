from app.bot.keyboards.reviews import reviews_queue_toolbar


def test_reviews_queue_toolbar_has_manual_and_history() -> None:
    buttons = reviews_queue_toolbar()
    callbacks = [b.callback_data for b in buttons]
    assert "review:manual:start" in callbacks
    assert "review:history" in callbacks
