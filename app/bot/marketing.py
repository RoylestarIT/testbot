"""Позиционирование vs рынок — без имён конкурентов."""

from app.bot.ui import (
    BRAND,
    VISUAL_SEP,
    brand_title,
    bullet,
    footer_hint,
    hero_quote,
    muted,
    quote,
    section,
)
from app.core.config import get_settings


def why_us_hub_text() -> str:
    settings = get_settings()
    lite = settings.subscription_lite_price_rub
    pro = settings.subscription_pro_price_rub
    lite_byn = settings.subscription_lite_price_byn
    pro_byn = settings.subscription_pro_price_byn
    return (
        brand_title(
            "Почему мы",
            tagline="Время, деньги и лояльность покупателей — в одном Telegram",
            icon="💡",
        )
        + VISUAL_SEP
        + "\n\n"
        + hero_quote(
            "Отзывы не должны съедать ваш день. "
            "«Голос бренда» забирает рутину: подтягиваем WB/Ozon, предлагаем 3 варианта ответа — "
            "вы решаете, что увидит покупатель."
        )
        + section("Экономия времени", icon="⏱")
        + "\n"
        + bullet("Очередь в Telegram: не прыгаете между кабинетами и таблицами")
        + "\n"
        + bullet("ИИ готовит черновики — правка и отправка за минуты, не за часы")
        + "\n"
        + bullet("PRO: publish в API и авто только на <b>4–5★</b> — позитив закрывается быстрее")
        + section("Экономия на людях", icon="💼")
        + "\n"
        + bullet(
            "Отдельный сотрудник «только на отзывы» — часто <b>30–80 тыс. ₽</b> и выше в месяц "
            "+ больничные и обучение"
        )
        + "\n"
        + bullet(
            f"Подписка <b>{lite} ₽</b> / <b>{pro} ₽</b> "
            f"(<b>{lite_byn:g}</b> / <b>{pro_byn:g} BYN</b>) — фикс, без оплаты за каждый ответ"
        )
        + "\n"
        + bullet("Один селлер или команда: бот не заменяет стратегию, но снимает ежедневную рутину")
        + section("Лояльность и продажи", icon="❤️")
        + "\n"
        + bullet("Покупатель видит, что бренд <b>живой</b> — ответ повышает доверие к карточке")
        + "\n"
        + bullet("Негатив <b>1–3★</b> только с вашего подтверждения — без «робота», который портит репутацию")
        + "\n"
        + bullet("Единый тон ответа — узнаваемый «голос» магазина на WB и Ozon")
        + section("Только для селлеров", icon="🎯")
        + "\n"
        + bullet("WB + Ozon в одном боте: sync, уведомления, история, калькулятор тарифа")
        + "\n"
        + bullet("Crypto / карта РФ·РБ — без лишних кабинетов на сайтах конкурентов")
        + "\n"
        + bullet("Вы контролируете текст — мы не «чёрный ящик» с автопубликацией всего подряд")
        + "\n\n"
        + muted("👇 Сравнение с рынком, «для кого» и карта функций — кнопками ниже.")
    )


def market_compare_text() -> str:
    settings = get_settings()
    lite_rub = settings.subscription_lite_price_rub
    pro_rub = settings.subscription_pro_price_rub
    return (
        brand_title("Сравнение с рынком", tagline="Честно: мы vs типичные сервисы", icon="📊")
        + VISUAL_SEP
        + "\n\n"
        + section("Формат", icon="📱")
        + "\n"
        + bullet("✅ <b>Мы</b> — co-pilot в Telegram: sync → ответы → publish или копия")
        + "\n"
        + bullet("⚪ <b>Часто</b> — отдельный сайт, только WB или перегруженный SaaS")
        + section("Деньги и масштаб", icon="💵")
        + "\n"
        + bullet(f"✅ <b>Мы</b> — <b>{lite_rub} / {pro_rub} ₽</b> в месяц, без «1 ₽ за ответ»")
        + "\n"
        + bullet("⚪ <b>Часто</b> — pay-per-answer или тарифы 2 500–12 000 ₽ без Ozon")
        + section("Контроль и риск", icon="✋")
        + "\n"
        + bullet("✅ <b>3 варианта ИИ</b>, правка вручную; негатив не уходит в автомат")
        + "\n"
        + bullet("⚪ Шаблоны или полный автомат на все звёзды")
        + section("PRO", icon="🚀")
        + "\n"
        + bullet("✅ Publish в API из бота · авто только <b>4–5★</b>")
        + "\n"
        + bullet("⚪ Авто «на всё» или publish только с десктопа")
        + section("Старт", icon="🎁")
        + "\n"
        + bullet(f"✅ Trial PRO <b>{settings.trial_pro_days}</b> дн. — кнопка на сводке")
        + "\n"
        + bullet("⚪ Разовые «N бесплатных ответов» без полного цикла")
        + footer_hint(f"{BRAND} · отзывы = время + лояльность · WB + Ozon")
    )


def for_whom_text() -> str:
    settings = get_settings()
    return (
        brand_title(
            "Для кого",
            tagline="Селлерам, для которых отзывы — часть выручки",
            icon="🎯",
        )
        + VISUAL_SEP
        + "\n\n"
        + hero_quote(
            "Если отзывов больше, чем часов в сутках — вам нужен не ещё один табличный сервис, "
            "а помощник, который ускоряет ответы и не ломает репутацию на негативе."
        )
        + section("Идеальный профиль", icon="✅")
        + "\n"
        + bullet("🛒 <b>Селлер WB/Ozon</b> — от ~30 до сотен отзывов в месяц")
        + "\n"
        + bullet("👤 Работаете сами или маленькая команда — некому «сидеть в отзывах» целый день")
        + "\n"
        + bullet("📱 Хотите всё из Telegram: уведомление → ответ → publish или копия")
        + "\n"
        + bullet("✋ Важен контроль: негатив и спорные формулировки — только вы")
        + section("Что вы получите", icon="💎")
        + "\n"
        + quote(
            "▸ Меньше рутины — больше времени на закупки, рекламу и ассортимент\n"
            "▸ Быстрее закрываете очередь — карточки выглядят «живыми» для покупателя\n"
            "▸ Предсказуемые расходы: "
            f"<b>{settings.subscription_lite_price_rub} / {settings.subscription_pro_price_rub} ₽</b> "
            "вместо штатной ставки или пакетов «за каждый клик»\n"
            "▸ PRO: автоматизация позитива без риска на 1–3★"
        )
        + section("С чем мы усиливаем селлера", icon="⚡")
        + "\n"
        + bullet("Синхронизация и напоминания — ничего не «зависает» неделями")
        + "\n"
        + bullet("Тон бренда и стоп-слова — ответы звучат как вы, не как случайный шаблон")
        + "\n"
        + bullet("Аналитика на «Подробнее» — видите динамику publish vs ручных ответов")
        + section("Скорее не к нам", icon="➖")
        + "\n"
        + bullet("Нужен только Я.Маркет или тяжёлая BI без работы с отзывами")
        + "\n"
        + bullet("Хотите 100% автомат на все отзывы без участия человека")
        + "\n\n"
        + muted("Готовы попробовать? Сводка → Trial PRO или «Подписка».")
    )


def feature_roadmap_text() -> str:
    return (
        brand_title("Функции", tagline="Честная карта: есть · скоро · не в фокусе", icon="🗺")
        + VISUAL_SEP
        + "\n\n"
        + section("✅ Уже работает", icon="")
        + "\n"
        + bullet("WB + Ozon, sync и уведомления")
        + "\n"
        + bullet("ИИ: 3 варианта, тон ответа, шаблоны 4–5★")
        + "\n"
        + bullet("Publish в API (PRO) и копия (Lite)")
        + "\n"
        + bullet("Авто только 4–5★; негатив — вручную")
        + "\n"
        + bullet("История, snooze, дайджест, CSV")
        + "\n"
        + bullet("Вопросы WB (push) · правила авто · калькулятор тарифа")
        + section("🔜 В приоритете", icon="")
        + "\n"
        + bullet("Мягкая рекомендация товара в ответе (PRO, по желанию)")
        + section("📋 По спросу", icon="")
        + "\n"
        + bullet("Очередь вопросов Ozon · NPS и время до ответа")
        + section("⛔ Не в фокусе", icon="")
        + "\n"
        + bullet("Яндекс Маркет · автомат на 1–3★ · отдельный web вместо Telegram")
    )
