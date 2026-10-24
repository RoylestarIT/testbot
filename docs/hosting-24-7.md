# Бот 24/7

Сайт живёт на **GitHub Pages**. Бот — только на **вашем сервере** (VPS).

## Почему не Cloud Agent

Среда, в которой работает Cursor Cloud Agent, **не предназначена для продакшена**: VM выключается, когда агент не активен. Запуск через `nohup` или вручную здесь — для тестов, не для пользователей 24/7.

## Что нужно на VPS

1. **Ubuntu 22.04/24.04** (или другой Linux с **systemd**).
2. Репозиторий, `.env` (те же секреты, что сейчас: `BOT_TOKEN`, `FERNET_KEY`, `DATABASE_URL`, `FSM_REDIS_URL`, …).
3. **PostgreSQL** и **Redis** на том же сервере (или managed DB + Redis в облаке).
4. Один процесс бота на один `BOT_TOKEN` (polling **или** webhook с HTTPS, не оба).

## Установка (один раз)

```bash
cd /opt/reviewpilot   # путь к клону
cp .env.example .env  # заполнить
sudo apt install -y postgresql redis-server python3-venv  # при необходимости
./scripts/ensure-datastores.sh
python3 -m alembic upgrade head
./scripts/install-systemd.sh
```

Проверка:

```bash
curl -s localhost:8081/health | python3 -m json.tool
journalctl -u reviewpilot -f
```

## После обновления кода

```bash
git pull
./scripts/restart-bot.sh   # при включённом systemd — systemctl restart
```

## Бэкапы

```bash
./scripts/backup-db.sh /var/backups/reviewpilot
```

Пример cron: `scripts/cron-backup.example`.

## Webhook (по желанию)

Домен с TLS → nginx/caddy → `WEBHOOK_URL=https://ваш-домен/webhook`. Тогда бот не зависит от long polling и лучше переживает рестарты.
