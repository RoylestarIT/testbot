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
- **Health**: `GET http://localhost:8081/health` (если `HEALTH_PORT=8081`).

Перезапуск на VM: `./scripts/restart-bot.sh`  
Бэкап SQLite: `./scripts/backup-db.sh`

## Тарифы (кратко)

| | Бесплатно | Lite | PRO |
|---|:---:|:---:|:---:|
| Генерации/день | 5 | ∞ | ∞ |
| Кабинеты / tone | 1 / 1 | ∞ | ∞ |
| Publish в API | ✗ | ✗ | ✓ |

Подробно: **Подписка → Сравнение тарифов** в боте.

## Основные команды

- `/start` — сводка (дашборд), чеклист onboarding
- `/dashboard` — то же
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
