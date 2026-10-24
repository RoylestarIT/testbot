from app.db.models import User
from app.services.wb_questions_queue import filter_visible_questions, is_question_snoozed, snooze_question


def test_snooze_hides_question() -> None:
    user = User(id=1, tg_id=1)
    snooze_question(user, 10, "q123")
    assert is_question_snoozed(user, 10, "q123")
    items = [{"id": "q123", "text": "Размер?"}]
    assert filter_visible_questions(user, type("A", (), {"id": 10})(), items) == []
