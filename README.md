# ReviewPilot

Telegram-бот для селлеров Wildberries и Ozon: получает отзывы (или текст вручную) и помогает формулировать ответы в вашем tone of voice. Lite — полуавтомат с вариантами ответа; PRO — публикация через Seller API с модерацией негатива.

## Требования

- Python 3.11+

## Установка

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Заполните в `.env` как минимум `BOT_TOKEN` (токен от [@BotFather](https://t.me/BotFather)).

Для шифрования ключей маркетплейсов на следующих этапах сгенерируйте `FERNET_KEY`:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

## Миграции

Схема БД управляется Alembic. При старте бота миграции применяются автоматически (`alembic upgrade head`).

Вручную:

```bash
alembic upgrade head
alembic revision --autogenerate -m "описание изменений"
```

## Запуск

Из корня репозитория:

```bash
python -m app.main
```

## Проверка

1. Откройте бота в Telegram и отправьте `/start`.
2. Должно прийти приветствие и inline-меню: **Отзывы**, **Настройки**, **Подписка**, **Помощь**.
3. **Настройки** — подключение WB/Ozon API, профили tone of voice.
4. **Отзывы** — синхронизация с маркетплейсами и публикация ответа после подтверждения.

## Lite: ручной ввод отзыва

В боте: **Отзывы → Ответить на отзыв** — текст, оценка 1–5, выбор тона, три варианта ответа с кнопками «Опубликовать (Lite: скопируй)», «Ещё варианты», «Изменить тон». Записи сохраняются в `reviews` и `generated_replies`.

Лимит **Lite**: 5 генераций в день (1 генерация = 3 варианта). **PRO** — без лимита (активная подписка в БД).

## Подписка и оплата

- **Telegram Stars**: инвойсы Lite (~$10/мес) и PRO (~$30/мес) — `SUBSCRIPTION_*_STARS` в `.env`
- **QR (Беларусь)**: заявка → админ `/approve <subscription_id>` (ваш Telegram ID в `ADMIN_IDS`)
- Команда `/my_subscription` — статус тарифа

Для Stars-инвойсов в BotFather должны быть включены платежи (Telegram Stars).

## LLM (генерация ответов)

Сервис [`app/services/llm.py`](app/services/llm.py): `generate_replies(review_text, rating, tone_profile, count=3)`.

Требуется `OPENAI_API_KEY` в `.env`; для DeepSeek и других провайдеров укажите `OPENAI_BASE_URL` и `OPENAI_MODEL`.

Ответы проверяются валидатором [`app/services/reply_validation.py`](app/services/reply_validation.py) (без URL, контактов, запрещённых фраз).

## Маркетплейсы (WB / Ozon)

- Клиенты: [`app/services/marketplace/wildberries.py`](app/services/marketplace/wildberries.py) (Feedbacks API), [`app/services/marketplace/ozon.py`](app/services/marketplace/ozon.py).
- Подключение: **Настройки → + Wildberries / + Ozon** — ключ шифруется (`FERNET_KEY`), тестовый запрос «1 отзыв».
- **Отзывы → Синхронизировать отзывы** — ручной импорт неотвеченных отзывов в БД.
- Публикация на API: **только PRO** → «Опубликовать на WB/Ozon» → подтверждение. Lite — копирование текста вручную.
- **Авто-публикация (PRO)**: для 4–5★ — ответ без подтверждения; 1–3★ — только уведомление.
- Ozon: официальный `POST /v1/review/list` (`status: UNPROCESSED`), пагинация `last_id`.
- Фоновый poller: `POLL_INTERVAL_MINUTES` (по умолчанию 15), уведомление в Telegram о новых отзывах.

## Админ-команды

Telegram ID в `ADMIN_IDS`:

- `/stats` — пользователи, подписки, отзывы
- `/pending` — pending-платежи
- `/approve <id>` / `/reject <id>` — QR-заявки
- `/broadcast preview Текст` — число получателей и предпросмотр
- `/broadcast send Текст` — рассылка (с паузой 50 ms между сообщениями)

## Тесты

```bash
pytest
```

## Структура

См. каталог `app/` — handlers, services, db, core. Точка входа: `app/main.py`.
