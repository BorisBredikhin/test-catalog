# backend

FastAPI + Alembic (async SQLAlchemy / asyncpg) + PostgreSQL.

## Запуск

```bash
# 1. PostgreSQL (из корня репозитория)
docker compose up -d

# 2. Миграции
uv run alembic upgrade head

# 3. Сервер
uv run fastapi dev app/main.py
```

Swagger: http://localhost:8000/docs

## Миграции

```bash
uv run alembic revision --autogenerate -m "описание"
uv run alembic upgrade head
```

DATABASE_URL задаётся в `backend/.env` (см. `.env.example`).
