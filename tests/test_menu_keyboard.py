from app.bot.keyboards.menu import main_menu_keyboard


def test_main_menu_keyboard_has_four_buttons() -> None:
    markup = main_menu_keyboard()
    texts = [
        button.text
        for row in markup.inline_keyboard
        for button in row
    ]
    assert texts == ["Отзывы", "Настройки", "Подписка", "Помощь"]
