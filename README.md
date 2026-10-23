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

## Запуск

Из корня репозитория:

```bash
python -m app.main
```

## Проверка

1. Откройте бота в Telegram и отправьте `/start`.
2. Должно прийти приветствие и inline-меню: **Отзывы**, **Настройки**, **Подписка**, **Помощь**.
3. Кнопки «Помощь» и заглушки разделов отвечают текстом (без реальных интеграций).

## Тесты

```bash
pytest
```

## Структура

См. каталог `app/` — handlers, services, db, core. Точка входа: `app/main.py`.
