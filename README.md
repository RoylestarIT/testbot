# ReviewPilot

Telegram-бот для селлеров **Wildberries** и **Ozon**: синхронизация отзывов, генерация ответов (LLM + tone of voice), публикация через Seller API на тарифе PRO.

## Требования

- Python 3.11+

## Установка

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Заполните `BOT_TOKEN`, при работе с кабинетами — `FERNET_KEY` и `OPENAI_API_KEY`.

## Миграции

При старте бота: `alembic upgrade head` (автоматически в `on_startup`).

```bash
alembic upgrade head
```

## Запуск

```bash
python3 -m app.main
```

- **Polling** (по умолчанию): если `WEBHOOK_URL` пуст.
- **Webhook**: задайте `WEBHOOK_URL=https://your.host/webhook` и проксируйте на `WEBHOOK_PORT`.
- **Health**: `GET http://localhost:8081/health` (если `HEALTH_PORT=8081`) — БД и статус poller (`poller.last_ok_minsk`).
- **FSM (prod)**: `FSM_REDIS_URL=redis://localhost:6379/0` — общее состояние диалогов для webhook/нескольких воркеров.
- **Дайджест**: `DIGEST_HOUR_UTC=6` (~9:00 Europe/Minsk), вкл. в «🔔 Уведомления».
- **LLM-очередь**: `LLM_QUEUE_WORKERS=2` — параллельные генерации без блокировки event loop.

Перезапуск на VM: `./scripts/restart-bot.sh`  
Бэкап SQLite: `./scripts/backup-db.sh`

## Тарифы (кратко)

| | Бесплатно | Lite | PRO |
|---|:---:|:---:|:---:|
| Генерации/день | 5 | ∞ | ∞ |
| Кабинеты / tone | 1 / 1 | ∞ | ∞ |
| Publish в API | 3 пробных | копия в кабинет | ✓ без лимита |

Подробно: **Подписка → Сравнение тарифов** в боте.  
Позиционирование vs рынок: **Сводка → ℹ️ Почему мы → Сравнение / Функции**. Backlog команды: [ROADMAP.md](ROADMAP.md).

### Crypto Bot (без Stars / без ИП)

```env
CRYPTO_PAY_API_TOKEN=...   # @CryptoBot → Crypto Pay → Create App
PAYMENT_ENABLE_STARS=false
CRYPTO_LITE_AMOUNT_USD=10
CRYPTO_PRO_AMOUNT_USD=20
```

В @CryptoBot включите **Webhooks** на `https://ВАШ_ДОМЕН:8081/cryptopay/webhook` (или путь из `CRYPTO_PAY_WEBHOOK_PATH`).  
Без публичного webhook оплата всё равно подтвердится через фоновый poller (~90 с) или кнопку «Проверить оплату».

## Профиль бота в Telegram

При каждом старте бот выставляет **краткое описание**, **описание** и **меню команд** (язык по умолчанию `ru`). Переопределение в `.env`:

- `BOT_SHORT_DESCRIPTION` — до 120 символов (карточка бота)
- `BOT_DESCRIPTION` — до 512 символов (экран до /start)
- `BOT_PROFILE_LANGUAGE=ru`

Команда `/admin` в меню видна только чатам из `ADMIN_IDS`.

## Основные команды

- `/start` — сводка (дашборд), чеклист onboarding
- `/dashboard` — то же
- `/help` — справка
- `/my_subscription` — статус тарифа
- `/promo КОД` — промокод (trial PRO)
- `/admin` — админ-панель (`ADMIN_IDS`)

## PostgreSQL (prod)

В `.env`:

```env
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/reviewpilot
```

Установите драйвер `asyncpg`, выполните мигraции на чистой БД.

## Структура

- `app/bot/` — handlers, keyboards, FSM
- `app/services/` — LLM, маркетплейсы, подписки, dashboard
- `app/tasks/` — poller WB/Ozon, напоминания о подписке
- `tests/` — pytest

```bash
python3 -m pytest -q
```
