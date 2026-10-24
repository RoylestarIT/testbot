"""Позиционирование vs рынок — без имён конкурентов."""

from app.bot.ui import BRAND, brand_title, bullet, footer_hint, muted, section
from app.core.config import get_settings


def market_compare_text() -> str:
    settings = get_settings()
    lite = settings.subscription_lite_usd_label
    pro = settings.subscription_pro_usd_label
    return (
        brand_title("Сравнение с рынком", tagline="Без названий — по типичным предложениям", icon="📊")
        + section("Формат", icon="📱")
        + "\n"
        + bullet("✅ Мы: co-pilot в <b>Telegram</b> — sync → ответы → publish или копия")
        + "\n"
        + bullet("⚪ Часто: отдельный <b>сайт</b> или только <b>WB</b> без Ozon")
        + section("Оплата", icon="💵")
        + "\n"
        + bullet(f"✅ Мы: <b>~${lite}</b> / <b>~${pro}</b> в месяц, без счёта «за каждый ответ»")
        + "\n"
        + bullet("⚪ Часто: 1–3 ₽ за ответ или тарифы от 2500–12000 ₽/мес")
        + section("Контроль", icon="✋")
        + "\n"
        + bullet("✅ Мы: <b>3 варианта ИИ</b>, вы правите; <b>1–3★ только вручную</b>")
        + "\n"
        + bullet("⚪ Часто: шаблоны или «авто на всё» без стопа на негативе")
        + section("PRO", icon="🚀")
        + "\n"
        + bullet("✅ Авто-ответы только <b>4–5★</b>; publish в API из бота")
        + "\n"
        + bullet("⚪ У многих полный автомат без разделения по звёздам")
        + section("Пробный доступ", icon="🎁")
        + "\n"
        + bullet(f"✅ Trial PRO — <b>{settings.trial_pro_days}</b> дней + publish-квота")
        + "\n"
        + bullet("⚪ У рынка: от 3 дней до «N бесплатных ответов»")
        + footer_hint(f"{BRAND} · WB + Ozon · crypto / карта РФ·РБ / юр. счёт")
    )


def feature_roadmap_text() -> str:
    return (
        brand_title("Функции", tagline="Честная карта: есть · скоро · не планируем", icon="🗺")
        + section("✅ Уже есть", icon="")
        + "\n"
        + bullet("WB + Ozon, sync и уведомления")
        + "\n"
        + bullet("ИИ: 3 варианта, tone, шаблоны 4–5★")
        + "\n"
        + bullet("Publish в API (PRO) и копия (Lite)")
        + "\n"
        + bullet("Авто только 4–5★; негатив — вручную")
        + "\n"
        + bullet("История, snooze, дайджест")
        + "\n"
        + bullet("Аналитика 7/30 дней на «Подробнее»")
        + "\n"
        + bullet("Подписка: crypto, карта, юр. безнал")
        + "\n"
        + bullet("CSV истории · правила авто (5★ / без текста) · push о вопросах WB")
        + section("🔜 Скоро (приоритет)", icon="")
        + "\n"
        + bullet("Опция «мягкая рекомендация» товара в ответе (PRO)")
        + section("📋 Дальше по спросу", icon="")
        + "\n"
        + bullet("Очередь «Вопросы покупателей» (WB → Ozon)")
        + "\n"
        + bullet("Расширенная аналитика (NPS, время до ответа)")
        + section("⛔ Не в фокусе", icon="")
        + "\n"
        + bullet("Яндекс Маркет (пока)")
        + "\n"
        + bullet("Полный автомат на 1–3★")
        + "\n"
        + bullet("Отдельный web-кабинет вместо Telegram")
    )
