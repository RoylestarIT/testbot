"""Тексты бота — единое место для тона и формулировок."""

from app.bot.ui import brand_title, bullet, footer_hint, muted, quote, section

WELCOME_TEXT = (
    brand_title("Добро пожаловать", tagline="Ответы на отзывы WB и Ozon в вашем стиле", icon="👋")
    + section("Тарифы", icon="💎")
    + "\n"
    + bullet("🆓 Free — до 5 генераций в день")
    + "\n"
    + bullet("✨ Lite — безлимит, ответ вручную в кабинете")
    + "\n"
    + bullet("🚀 PRO — publish из бота и авто-ответы 4–5★")
    + footer_hint("ReviewPilot не аффилирован с маркетплейсами.")
)

TERMS_TEXT = (
    brand_title("Условия использования", icon="📜")
    + "\n"
    + quote(
        "🔐 API-ключи хранятся в зашифрованном виде.\n"
        "📝 Тексты отзывов — только для генерации ответов.\n"
        "✍️ Вы отвечаете за публикуемые формулировки."
    )
    + "\n\n✅ Нажмите «Принимаю», чтобы продолжить."
)

HELP_TEXT = (
    brand_title("Справка", tagline="Кратко о возможностях", icon="📖")
    + section("Навигация", icon="🧭")
    + "\n"
    + bullet("🏠 /start — сводка")
    + "\n"
    + bullet("📋 «Полное меню» — все разделы")
    + section("Отзывы", icon="💬")
    + "\n"
    + bullet("📬 очередь и «Следующий отзыв»")
    + "\n"
    + bullet("⚡ готовые фразы для 4–5★")
    + "\n"
    + bullet("📚 история с фильтрами")
    + section("Тарифы", icon="💎")
    + "\n"
    + bullet("🆓 · ✨ · 🚀 — таблица в «Подписка»")
    + section("API", icon="🔑")
    + "\n"
    + bullet("🟣 WB — «Вопросы и отзывы»")
    + "\n"
    + bullet("🔵 Ozon — Client-Id + Api-Key")
    + section("Ещё", icon="➕")
    + "\n"
    + bullet("🔔 уведомления в Настройках")
    + "\n"
    + bullet("🎟 /promo — промокод")
    + footer_hint("⌨️ /start · /dashboard · /my_subscription")
)

REVIEWS_MENU_TEXT = (
    brand_title("Отзывы", tagline="Ручной ввод, sync и очередь", icon="💬")
    + "\n"
    + muted("👇 Выберите действие на клавиатуре")
)

SETTINGS_INTRO = (
    brand_title("Настройки", tagline="Кабинеты, tone, уведомления", icon="⚙️")
    + "\n"
    + quote(
        "🏪 Подключите WB/Ozon\n"
        "🎨 Настройте tone of voice\n"
        "🚀 Авто-публикация — на PRO"
    )
)

SYNC_INTRO = brand_title("Синхронизация", icon="🔄") + "\n" + muted("Выберите кабинет или обновите все")

SYNC_DONE = brand_title("Готово", icon="✅") + "\n" + "📬 Новых отзывов: <b>{count}</b>"

MP_LIST_EMPTY = brand_title("Очередь пуста", icon="📭") + "\n" + muted("🏪 Подключите кабинет или 🔄 sync")

MP_LIST_HEADER = brand_title("Новые отзывы", tagline="Выберите отзыв", icon="📬")

PUBLISH_SUCCESS = brand_title("Опубликовано", icon="✅") + "\n" + "🚀 Ответ ушёл на маркетплейс"

COPY_HINT = (
    brand_title("Скопируйте ответ", icon="📋")
    + "\n"
    + quote("{text}")
    + "\n"
    + muted("📎 Вставьте в кабинет продавца")
)

NEGATIVE_PUBLISH_WARN = (
    brand_title("Подтверждение", tagline="Низкая оценка", icon="⚠️")
    + "\n"
    + quote("{text}")
)

PRO_PUBLISH_REQUIRED = (
    "🚀 Publish в WB/Ozon — тариф <b>PRO</b> (trial или квота).\n\n"
    "📋 На Free и Lite — «Скопировать ответ»."
)

Ozon_FORBIDDEN_HINT = "\n\n" + muted("🔵 Ozon: часто нужен Premium Plus.")
