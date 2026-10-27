from app.services.generation_guard import is_generation_callback


def test_is_generation_callback() -> None:
    assert is_generation_callback("review:more") is True
    assert is_generation_callback("review:tone:default") is True
    assert is_generation_callback("review:tone:preset:grateful") is True
    assert is_generation_callback("review:sync") is False
    assert is_generation_callback("review:pick:0") is False
