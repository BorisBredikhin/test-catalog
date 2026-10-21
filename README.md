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

Команда `/start` отвечает кнопкой «Открыть каталог», если задан `WEBAPP_URL`.

## Mini App

Каталог открывается в Telegram как Mini App: по кнопке в сообщении бота и по
кнопке меню чата. Приложение получает `initData` — строку, подписанную
Telegram, — и отправляет её бэкенду, который проверяет подпись и возвращает
профиль пользователя.

### Настройка

1. Задеплойте фронтенд на публичный **HTTPS**-адрес (Telegram не открывает
   Mini App по `http://localhost`).
2. В [@BotFather](https://t.me/BotFather) → `/newapp` укажите этот адрес
   (или `Bot Settings → Configure Mini App`). Telegram проверяет, что адрес
   доступен извне.
3. Пропишите в `backend/.env` (и в `.env` в корне — он используется compose):

```bash
# Публичный HTTPS-URL фронтенда. Пусто — бот не показывает кнопку каталога.
WEBAPP_URL=https://catalog.example.com
# Не проверять подпись initData. Только для локальной разработки!
WEBAPP_DEV=false
```

### Локальная разработка

Telegram не отдаёт `initData` за пределами Telegram, поэтому локально
подставляем поддельные, но корректно подписанные данные.

Сгенерировать `initData` (нужен `BOT_TOKEN`):

```bash
cd backend
uv run python scripts/make_init_data.py 111111111 --first-name Ivan
```

Открыть каталог с этой подменой:

```bash
# в корне репозитория
NEXT_PUBLIC_TELEGRAM_INIT_DATA='<initData>' pnpm --dir frontend dev
```

или передать `initData` прямо в адресной строке:

```
http://localhost:3000/?tgWebAppData=<initData>
```

Фронтенд в этом случае считает, что запущен внутри Telegram: применяет тему,
разворачивает на всю высоту и показывает пользователя. Бэкенду `initData`
уходит в заголовке `X-Telegram-Init-Data`, подпись проверяется как обычно.

Чтобы обойтись вообще без `initData` (например, для curl-тестов), включите
`WEBAPP_DEV=true` — тогда backend подставит тестового пользователя.

```bash
curl -H "X-Telegram-Init-Data: $INIT_DATA" http://localhost:8000/me
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
