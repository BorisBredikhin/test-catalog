# backend

FastAPI + Alembic (async SQLAlchemy / asyncpg) + PostgreSQL + Telegram-бот (aiogram) + MinIO.

## Запуск

```bash
# 1. PostgreSQL и MinIO (из корня репозитория)
docker compose up -d

# 2. Миграции
uv run alembic upgrade head

# 3. Сервер (бот стартует вместе с приложением)
uv run fastapi dev app/main.py
```

Swagger: http://localhost:8000/docs

## Бот

Бот запускается в том же процессе, что и FastAPI (в `lifespan`).

1. Создайте бота у [@BotFather](https://t.me/BotFather), получите токен.
2. Узнайте свой telegram id (например, у [@userinfobot](https://t.me/userinfobot)).
3. Пропишите в `backend/.env`:

```bash
BOT_TOKEN=123456:ABC-...
ADMIN_IDS=111111111,222222222
```
## MinIO

Официальные Docker-образы `minio/minio` удалены с Docker Hub/Quay, поэтому
сервис `minio` собирается из исходников (см. `minio/Dockerfile`; версия
фиксируется build-аргументом `MINIO_RELEASE` в compose). Первый `docker compose
up --build` долго собирает бинарник.

Консоль: http://localhost:9001 (логин/пароль `minioadmin`). Бакет создаётся
автоматически при старте приложения. Фото хранятся в бакете `catalog` под
путём `products/<uuid>.jpg`; публичный URL собирается из `MINIO_PUBLIC_URL`.

## Миграции

```bash
uv run alembic revision --autogenerate -m "описание"
uv run alembic upgrade head
```

DATABASE_URL задаётся в `backend/.env` (см. `.env.example`).

## Разработка

```bash
docker compose -f compose.dev.yml up
```
