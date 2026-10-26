from app.bot.keyboards.menu import (
    dashboard_keyboard,
    main_menu_keyboard,
    more_menu_keyboard,
)
from app.bot.ui import REVIEWS_HUB_BUTTON


def test_main_menu_keyboard_has_reviews_hub() -> None:
    markup = main_menu_keyboard()
    texts = [button.text for row in markup.inline_keyboard for button in row]
    assert REVIEWS_HUB_BUTTON in texts
    assert "🏠 Сводка" in texts
    assert "📬 Очередь" not in texts


def test_more_menu_only_help_support() -> None:
    markup = more_menu_keyboard()
    texts = [button.text for row in markup.inline_keyboard for button in row]
    callbacks = [button.callback_data for row in markup.inline_keyboard for button in row]
    assert "🆘 Поддержка" in texts
    assert "📖 Справка" in texts
    assert "review:sync" not in callbacks
    assert "review:mp:list" not in callbacks
    assert "menu:why_us" in callbacks
    assert "menu:wb_questions" in callbacks
    assert "menu:service_status" not in callbacks
    assert "menu:changelog" in callbacks


def test_more_menu_shows_admin_for_admins() -> None:
    markup = more_menu_keyboard(show_admin=True)
    texts = [button.text for row in markup.inline_keyboard for button in row]
    assert "🛠 Админ" in texts


def test_dashboard_keyboard_primary_reviews_hub() -> None:
    kb = dashboard_keyboard(show_trial=False, show_onboarding=False, show_admin=False)
    first = kb.inline_keyboard[0][0].text
    assert first == REVIEWS_HUB_BUTTON


def test_dashboard_keyboard_compact_secondary_actions() -> None:
    kb = dashboard_keyboard(show_trial=False, show_onboarding=False, show_admin=False)
    callbacks = [button.callback_data for row in kb.inline_keyboard for button in row]
    assert "menu:why_us" not in callbacks
    assert "menu:wb_questions" not in callbacks
    assert "menu:dashboard:details" in callbacks
    assert "review:sync" in callbacks
