from app.bot.keyboards.menu import dashboard_keyboard, main_menu_keyboard


def test_main_menu_keyboard_has_core_sections() -> None:
    markup = main_menu_keyboard()
    texts = [
        button.text
        for row in markup.inline_keyboard
        for button in row
    ]
    assert "📬 Очередь" in texts
    assert "⚙️ Настройки" in texts
    assert "🏠 Сводка" in texts


def test_main_menu_keyboard_shows_admin_for_admins() -> None:
    markup = main_menu_keyboard(show_admin=True)
    texts = [button.text for row in markup.inline_keyboard for button in row]
    assert "🛠 Админ" in texts


def test_dashboard_keyboard_primary_queue() -> None:
    kb = dashboard_keyboard(show_trial=False, show_onboarding=False, show_admin=False)
    first = kb.inline_keyboard[0][0].text
    assert "Ответить" in first or "Очередь" in first
