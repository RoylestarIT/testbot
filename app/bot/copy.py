"""Тексты бота — единое место для тона и формулировок."""

from app.bot.ui import brand_title, bullet, footer_hint, muted, quote, section

WELCOME_TEXT = (
    brand_title("Добро пожаловать", tagline="Ответы на отзывы WB и Ozon в вашем стиле")
    + section("Тарифы")
    + "\n"
    + bullet("Free — до 5 генераций в день")
    + "\n"
    + bullet("Lite — безлимит генераций, ответ вручную в кабинете")
    + "\n"
    + bullet("PRO — публикация из бота и авто-ответы 4–5★")
    + footer_hint("ReviewPilot не аффилирован с маркетплейсами.")
)

TERMS_TEXT = (
    brand_title("Условия использования")
    + "\n"
    + quote(
        "API-ключи хранятся в зашифрованном виде.\n"
        "Тексты отзывов используются только для генерации ответов.\n"
        "Вы несёте ответственность за публикуемые формулировки."
    )
    + "\n\nНажмите «Принимаю», чтобы продолжить."
)

HELP_TEXT = (
    brand_title("Справка", tagline="Кратко о возможностях")
    + section("Навигация")
    + "\n"
    + bullet("/start — сводка и быстрые действия")
    + "\n"
    + bullet("«Полное меню» — все разделы")
    + section("Отзывы")
    + "\n"
    + bullet("Очередь новых отзывов и «Следующий»")
    + "\n"
    + bullet("⚡ готовые фразы для 4–5★")
    + "\n"
    + bullet("История с фильтрами publish / копия")
    + section("Тарифы")
    + "\n"
    + bullet("Free · Lite · PRO — таблица в «Подписка»")
    + section("API маркетплейсов")
    + "\n"
    + bullet("WB — ключ «Вопросы и отзывы»")
    + "\n"
    + bullet("Ozon — Client-Id + Api-Key (часто Premium Plus)")
    + section("Прочее")
    + "\n"
    + bullet("🔔 уведомления — в Настройках")
    + "\n"
    + bullet("/promo — промокод на trial PRO")
    + footer_hint("Команды: /start · /dashboard · /my_subscription")
)

REVIEWS_MENU_TEXT = (
    brand_title("Отзывы", tagline="Ручной ввод, синхронизация и очередь")
    + "\n"
    + muted("Выберите действие на клавиатуре ниже.")
)

SETTINGS_INTRO = (
    brand_title("Настройки", tagline="Кабинеты, tone of voice, уведомления")
    + "\n"
    + quote(
        "Free: 1 кабинет и 1 tone-профиль.\n"
        "Lite и PRO — без лимитов.\n"
        "Авто-публикация доступна на PRO."
    )
)

SYNC_INTRO = brand_title("Синхронизация") + "\n" + muted("Выберите кабинет или обновите все сразу.")

SYNC_DONE = brand_title("Готово") + "\n" + "Новых отзывов: <b>{count}</b>"

MP_LIST_EMPTY = (
    brand_title("Очередь пуста")
    + "\n"
    + muted("Подключите кабинет или запустите синхронизацию.")
)

MP_LIST_HEADER = brand_title("Новые отзывы", tagline="Выберите отзыв для ответа")

PUBLISH_SUCCESS = brand_title("Опубликовано") + "\n" + "Ответ отправлен на маркетплейс."

COPY_HINT = (
    brand_title("Скопируйте ответ")
    + "\n"
    + quote("{text}")
    + "\n"
    + muted("Вставьте текст в кабинет продавца.")
)

NEGATIVE_PUBLISH_WARN = (
    brand_title("Подтверждение", tagline="Низкая оценка — проверьте текст")
    + "\n"
    + quote("{text}")
)

PRO_PUBLISH_REQUIRED = (
    "Публикация в WB/Ozon из бота — на тарифе <b>PRO</b> "
    "(trial PRO или бесплатная квота).\n\n"
    "На Free и Lite используйте «Скопировать ответ»."
)

Ozon_FORBIDDEN_HINT = (
    "\n\n"
    + muted("Ozon: часто нужен Premium Plus и модуль «Отзывы».")
)
