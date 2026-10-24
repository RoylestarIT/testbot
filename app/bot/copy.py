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
            + bullet("📱 Очередь и publish — в Telegram, без отдельного сайта")
            + "\n"
            + bullet("✋ 1–3★ только вручную; авто-ответы — 4–5★ на PRO")
            + "\n"
            + bullet("💵 Подписка ~$10 / ~$20, не пакеты «за каждый ответ»")
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
        + bullet("💵 Фикс ~$10 (Lite) / ~$20 (PRO) в месяц вместо счёта за тысячи токенов")
        + "\n"
        + bullet("🪙 Crypto Bot и перевод РФ/РБ — без Stars и без ИП у селлера")
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
    + bullet("⋯ на сводке — только справка и поддержка")
    + "\n"
    + bullet("🔔 уведомления в Настройках")
    + "\n"
    + bullet("🎟 /promo — промокод")
    + differentiators_section(compact=True)
    + footer_hint("⌨️ /start · /dashboard · /my_subscription")
)

REVIEWS_MENU_TEXT = (
    brand_title("Отзывы", tagline="Ответы на отзывы WB/Ozon", icon="💬")
    + "\n"
    + muted("👇 Выберите действие на клавиатуре")
)

SETTINGS_INTRO = (
    brand_title("Настройки", tagline="Кабинеты WB/Ozon, tone, уведомления", icon="⚙️")
    + "\n"
    + quote(
        "🏪 Подключите WB/Ozon\n"
        "🎨 Настройте tone of voice\n"
        "🚀 Авто-публикация — на PRO"
    )
)

SYNC_INTRO = brand_title("Синхронизация", icon="🔄") + "\n" + muted("Выберите кабинет или обновите все")

SYNC_DONE = brand_title("Готово", icon="✅") + "\n" + "📬 Новых отзывов: <b>{count}</b>"

MP_LIST_EMPTY = (
    brand_title("Нет новых отзывов", icon="📭")
    + "\n"
    + muted("🔄 Sync (или ждите авто-sync) · ✍️ ручной ответ на этом экране")
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
