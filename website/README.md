# Лендинг «Голос бренда»

Маркетинговый сайт для Telegram-бота [@FeedBackReview_bot](https://t.me/FeedBackReview_bot).  
Техническое имя репозитория бота: **ReviewPilot**. На лендинге в footer указано мелко.

## Стек

- **Next.js 15** (App Router)
- **TypeScript**
- **Tailwind CSS**
- **Статический экспорт** (`output: "export"`) — деплой на Vercel, Cloudflare Pages, S3+CDN и т.п.

## Быстрый старт

```bash
cd website
cp .env.example .env.local   # при необходимости
npm install
npm run dev
```

Откройте [http://localhost:3000](http://localhost:3000).

## Сборка

```bash
npm run build
```

Артефакт: каталог `out/`.

## Переменные окружения

| Переменная | Описание |
|------------|----------|
| `NEXT_PUBLIC_SITE_URL` | Канонический URL сайта (Open Graph, sitemap). Пример: `https://golos-brenda.ru` |
| `NEXT_PUBLIC_BOT_URL` | Deep link бота. По умолчанию `https://t.me/FeedBackReview_bot` |
| `NEXT_PUBLIC_SUPPORT_EMAIL` | Email на странице контактов (placeholder до продакшена) |
| `NEXT_PUBLIC_LEGAL_OPERATOR_NAME` | Полное наименование ИП/ООО для `/privacy` и `/terms` |

Для бота (отдельный сервис) те же смыслы:

- `PRIVACY_POLICY_URL` → `{SITE_URL}/privacy`
- `TERMS_OF_SERVICE_URL` → `{SITE_URL}/terms`

## Структура страниц

| URL | Назначение |
|-----|------------|
| `/` | Главная: hero, УТП, шаги, тарифы, FAQ |
| `/pricing` | Таблица тарифов + сравнение с рынком |
| `/how-it-works` | 4 шага + mockup Telegram |
| `/for-who` | ЦА и блок «Скорее не к нам» |
| `/why-us` | Почему мы / экономика |
| `/faq` | Accordion |
| `/contacts` | Бот + email |
| `/privacy`, `/terms` | Юридические черновики |
| `/changelog` | Опционально, синхрон с «Что нового» в боте |

CTA везде ведёт в бота; для рекламы используется `?start=site` (см. `BOT_URL_SITE` в `src/lib/constants.ts`).

## Деплой

### Vercel

1. Root Directory: `website`
2. Build Command: `npm run build`
3. Output Directory: `out`
4. Задать env из таблицы выше

### Cloudflare Pages

- Framework preset: Next.js (Static HTML Export) или custom: `npm run build`, output `out`

После деплоя обновите `public/robots.txt` (строка `Sitemap:`) или генерируйте robots при сборке.

## Что уточнить у заказчика

- [ ] Домен и favicon/logo (сейчас placeholder «ГБ»)
- [ ] `NEXT_PUBLIC_LEGAL_OPERATOR_NAME` — ИНН, адрес, контакты для документов
- [ ] `PRIVACY_POLICY_URL` / `TERMS_OF_SERVICE_URL` в env бота
- [ ] Реальные скриншоты бота (после NDA)
- [ ] Яндекс.Метрика / GA4 ID (подключить в `layout.tsx` при необходимости)
- [ ] Нужен ли английский язык (по умолчанию — только RU)

## Ограничения контента (compliance)

- Не обещаем 100% автоматизацию всех отзывов и негатива
- Не заявляем партнёрство с WB/Ozon без документов
- API-ключи на лендинге не собираем
- Цены с пометкой «актуально в боте» + дата в footer (`PRICING_UPDATED`)
