from app.bot.handlers.onboarding import _STEP_META


def test_tone_step_opens_settings_tone() -> None:
    title, _, callback = _STEP_META[2]
    assert title == "Тон ответа"
    assert callback == "settings:tone"
