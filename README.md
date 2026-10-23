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
3. Кнопки «Помощь» и заглушки разделов отвечают текстом (без реальных интеграций).

## Lite: ручной ввод отзыва

В боте: **Отзывы → Ответить на отзыв** — текст, оценка 1–5, выбор тона, три варианта ответа с кнопками «Опубликовать (Lite: скопируй)», «Ещё варианты», «Изменить тон». Записи сохраняются в `reviews` и `generated_replies`.

Лимит **Lite**: 5 генераций в день (1 генерация = 3 варианта). **PRO** — без лимита (активная подписка в БД).

## LLM (генерация ответов)

Сервис [`app/services/llm.py`](app/services/llm.py): `generate_replies(review_text, rating, tone_profile, count=3)`.

Требуется `OPENAI_API_KEY` в `.env`; для DeepSeek и других провайдеров укажите `OPENAI_BASE_URL` и `OPENAI_MODEL`.

Ответы проверяются валидатором [`app/services/reply_validation.py`](app/services/reply_validation.py) (без URL, контактов, запрещённых фраз).

## Тесты

```bash
pytest
```

## Структура

См. каталог `app/` — handlers, services, db, core. Точка входа: `app/main.py`.
