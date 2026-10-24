"""Тексты бота — единое место для тона и формулировок."""

from app.bot.ui import BRAND, brand_title, bullet, footer_hint, muted, quote, section

# Позиционирование vs «большие платформы» (без названий конкурентов)
DIFFERENTIATORS_TAGLINE = (
    "Co-pilot в Telegram: WB/Ozon, вы решаете, что увидит покупатель"
)

DIFFERENTIATORS_DASHBOARD_LINE = muted("✋ Негатив — вручную · авто только 4–5★ (PRO)")


def differentiators_section(*, compact: bool = False) -> str:
    """Блок «Почему мы» для welcome, help, подписки."""
    if compact:
        return (
            section("Почему мы", icon="⚡")
            + "\n"
            + bullet("⏱ Меньше рутины — ответы из Telegram, не целый день в кабинете")
            + "\n"
            + bullet("💼 Фикс 800 / 1 600 ₽ вместо штатного «менеджера на отзывы»")
            + "\n"
            + bullet("❤️ Быстрые ответы → доверие к карточке; негатив — только вы")
            + "\n"
            + bullet("ℹ️ Подробнее: сводка → «Почему мы»")
        )
    return (
        section(f"Почему {BRAND}", icon="⚡")
        + "\n"
        + bullet("📱 Весь цикл в Telegram: sync → очередь → 3 варианта → publish или копия")
        + "\n"
        + bullet("✋ Вы выбираете и правите текст — не «чёрный ящик» с автопубликацией всего подряд")
        + "\n"
        + bullet("🛡 Негатив 1–3★ не уходит в автомат; авто-ответы только 4–5★ (PRO)")
        + "\n"
        + bullet("💵 Фикс 800 ₽ (Lite) / 1 600 ₽ (PRO) и 30 / 60 BYN в месяц")
        + "\n"
        + bullet("⭐ Telegram Stars, 🪙 Crypto Bot и перевод РФ/РБ — без ИП у селлера")
        + "\n"
        + bullet("🎯 Только отзывы WB/Ozon — без лишних модулей, быстрее разобраться")
    )


WELCOME_TEXT = (
    brand_title("Добро пожаловать", tagline=DIFFERENTIATORS_TAGLINE, icon="👋")
    + differentiators_section(compact=True)
    + section("Тарифы", icon="💎")
    + "\n"
    + bullet("🆓 Free — до 5 генераций в день")
    + "\n"
    + bullet("✨ Lite — без лимита генераций, ответ вручную в кабинете")
    + "\n"
    + bullet("🚀 PRO — publish из бота и авто-ответы 4–5★")
    + footer_hint(
        f"{BRAND} не связан с маркетплейсами. "
        "Помогаем быстро ответить на отзывы WB/Ozon под вашим контролем."
    )
)

TERMS_TEXT = (
    brand_title("Перед началом работы", tagline="Условия и персональные данные", icon="📜")
    + "\n\n"
    + section("Что делает бот", icon="✨")
    + "\n"
    + bullet("Синхронизирует отзывы WB/Ozon и помогает готовить ответы с ИИ")
    + "\n"
    + bullet("Публикует ответы в кабинет только по вашему действию (PRO)")
    + "\n\n"
    + section("Персональные данные", icon="🔒")
    + "\n"
    + bullet("Telegram ID, @username — аккаунт и поддержка")
    + "\n"
    + bullet("Тексты отзывов и ваши ответы — генерация и история")
    + "\n"
    + bullet("API-ключи маркетплейсов — храним в зашифрованном виде (Fernet)")
    + "\n"
    + bullet("Для ИИ-ответов текст отзыва передаётся провайдеру LLM (OpenAI-совместимый API)")
    + "\n\n"
    + section("Ваша ответственность", icon="✍️")
    + "\n"
    + bullet("Вы проверяете и утверждаете формулировки перед публикацией")
    + "\n"
    + bullet(f"{BRAND} не аффилирован с Wildberries и Ozon")
    + "\n\n"
    + muted(
        "Нажимая «Принимаю», вы соглашаетесь с обработкой данных для работы сервиса "
        "и принимаете условия использования."
    )
)

HELP_TEXT = (
    brand_title("Справка", tagline="Кратко о возможностях", icon="📖")
    + section("Навигация", icon="🧭")
    + "\n"
    + bullet("🏠 /start — сводка и быстрые кнопки")
    + "\n"
    + bullet("📬 «Ответы на отзывы» — главный раздел на сводке")
    + section("Отзывы", icon="💬")
    + "\n"
    + bullet("📬 WB/Ozon, ручной ввод и «Следующий отзыв»")
    + "\n"
    + bullet("✍️ ручной ответ — внутри «Ответы на отзывы»")
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
    + bullet("ℹ️ «Почему мы» — сравнение с рынком и карта функций")
    + "\n"
    + bullet("⋯ на сводке — справка, поддержка, 📜 документы")
    + "\n"
    + bullet("📜 /legal — политика конфиденциальности и условия сервиса")
    + "\n"
    + bullet("🔔 уведомления в Настройках")
    + "\n"
    + differentiators_section(compact=True)
    + footer_hint("⌨️ /start · /dashboard · /legal · /my_subscription")
)

REVIEWS_MENU_TEXT = (
    brand_title("Отзывы", tagline="Ответы на отзывы WB/Ozon", icon="💬")
    + "\n"
    + muted("👇 Выберите действие на клавиатуре")
)

SETTINGS_INTRO = (
    brand_title("Настройки", tagline="Кабинеты WB/Ozon, тон ответа, уведомления", icon="⚙️")
    + "\n"
    + quote(
        "🏪 Подключите WB/Ozon\n"
        "🎨 Настройте тон ответа\n"
        "🚀 Авто-публикация — на PRO"
    )
)

NOTIFICATIONS_INTRO = (
    brand_title("Уведомления", tagline="Push от синхронизации", icon="🔔")
    + "\n\n"
    + "▸ <b>Новые отзывы</b> — при появлении в очереди\n\n"
    + "▸ <b>Только негатив</b> — только 1–3★\n\n"
    + "▸ <b>Утренний дайджест</b> — сводка (~9:00 Минск)\n\n"
    + "▸ <b>Напоминание об очереди</b> — если без ответа &gt; 24 ч (~18:00 Минск)\n\n"
    + "▸ <b>Вопросы в кабинете</b> — новые вопросы WB без ответа\n\n"
    + "▸ <b>Мягкая рекомендация</b> — фраза о линейке в ИИ-ответах (Lite/PRO)\n\n"
    + muted("Ниже — переключатели. Изменения сохраняются сразу.")
)

MP_NO_CABINETS = (
    brand_title("Ответы на отзывы", tagline="Подключите WB или Ozon", icon="📬")
    + "\n\n"
    + "Кабинет маркетплейса пока не подключён — отзывы подтянутся после API-ключа.\n\n"
    + muted("Можно сразу ответить вручную — без кабинета.")
)

SYNC_INTRO = brand_title("Синхронизация", icon="🔄") + "\n" + muted("Выберите кабинет или обновите все")

SYNC_DONE = brand_title("Готово", icon="✅") + "\n" + "📬 Новых отзывов: <b>{count}</b>"

MP_LIST_EMPTY = (
    brand_title("Нет новых отзывов", icon="📭")
    + "\n"
    + muted("👇 🔄 Sync или ✍️ ручной ответ на этом экране")
)

MP_LIST_HEADER = brand_title("Ответы на отзывы", tagline="WB/Ozon · ручной ввод", icon="📬")

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
    "🚀 <b>Publish в API</b> — тариф PRO (trial или квота).\n\n"
    f"{BRAND} не публикует вслепую: на PRO в автомат уходят только <b>4–5★</b>, "
    "негатив — только после вашего подтверждения.\n\n"
    "📋 На Free и Lite — «Скопировать ответ» в кабинет."
)

Ozon_FORBIDDEN_HINT = "\n\n" + muted("🔵 Ozon: часто нужен Premium Plus.")
