from app.services.poller_notify import PollerUserNotify, build_poller_notify_text


def test_poller_notify_negative_only_filters_positives() -> None:
    stats = PollerUserNotify(auto_published=2, queue_new=0, queue_negative=0)
    assert build_poller_notify_text(stats=stats, negative_only=True) is None


def test_poller_notify_shows_auto_and_queue() -> None:
    stats = PollerUserNotify(
        auto_published=2,
        queue_new=1,
        queue_negative=1,
        auto_previews=["Спасибо за покупку!"],
    )
    text = build_poller_notify_text(stats=stats, negative_only=False)
    assert text is not None
    assert "Авто-ответов" in text
    assert "В очереди" in text
    assert "негатив" in text.lower()
