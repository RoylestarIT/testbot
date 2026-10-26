from app.bot.handlers.onboarding import _STEP_META


def test_quick_start_has_three_steps() -> None:
    assert len(_STEP_META) == 3


def test_tone_step_opens_settings_tone() -> None:
    title, _, callback = _STEP_META[2]
    assert title == "Тон ответа"
    assert callback == "settings:tone"
