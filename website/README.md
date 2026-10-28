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
| `NEXT_PUBLIC_YM_ID` | ID счётчика Яндекс.Метрики (число) |
| `NEXT_PUBLIC_GA_ID` | ID Google Analytics 4 (`G-…`) |

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

CTA везде ведёт в бота; для рекламы используется `?start=site` (см. `BOT_URL_SITE` в `src/content/constants.ts`).

## Деплой

### Vercel (рекомендуется)

1. Откройте [Import в Vercel](https://vercel.com/new/import?s=https%3A%2F%2Fgithub.com%2FRoylestarIT%2Ftestbot&root-directory=website&project-name=golos-brenda) (репозиторий `RoylestarIT/testbot`).
2. **Root Directory:** `website` (важно: в корне репозитория — Python-бот).
3. Framework: **Next.js** (подхватится из `vercel.json`).
4. Deploy. Preview-URL появится после первой сборки (`*.vercel.app`).
5. **Production env** (Settings → Environment Variables):
   - `NEXT_PUBLIC_SITE_URL` — ваш домен или `https://<project>.vercel.app`
   - `NEXT_PUBLIC_LEGAL_OPERATOR_NAME`, `NEXT_PUBLIC_SUPPORT_EMAIL` — перед публичным запуском
6. После деплоя пропишите в боте `PRIVACY_POLICY_URL` и `TERMS_OF_SERVICE_URL`.

Без `NEXT_PUBLIC_SITE_URL` sitemap/OG на сборке Vercel используют `VERCEL_URL` автоматически.

**CLI** (если есть `VERCEL_TOKEN`):

```bash
cd website
npx vercel link
npx vercel --prod
```

### GitHub Pages

CI на каждый push в `main` (путь `website/**`) пушит сборку в ветку **`gh-pages`**.

**Один раз** (только владелец репо): [Settings → Pages](https://github.com/RoylestarIT/testbot/settings/pages) → Source **Deploy from a branch** → **`gh-pages`** / **`/`** → Save.

Публичный URL: **https://roylestarit.github.io/testbot/**

Локально: `npm run deploy:gh-pages` (нужны `git user.name` / `user.email`).

### Cloudflare Pages

- `npm run build`, output `out`

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
