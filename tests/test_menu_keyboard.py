from app.bot.keyboards.menu import main_menu_keyboard


def test_main_menu_keyboard_has_core_sections() -> None:
    markup = main_menu_keyboard()
    texts = [
        button.text
        for row in markup.inline_keyboard
        for button in row
    ]
    assert texts == [
        "🏠  Сводка",
        "💬  Отзывы",
        "⚙️  Настройки",
        "💎  Подписка",
        "🆘  Поддержка",
        "📖  Справка",
    ]


def test_main_menu_keyboard_shows_admin_for_admins() -> None:
    markup = main_menu_keyboard(show_admin=True)
    texts = [button.text for row in markup.inline_keyboard for button in row]
    assert "🛠  Админ" in texts
