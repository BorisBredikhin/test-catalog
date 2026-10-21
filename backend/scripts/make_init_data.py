"""Генерация валидной initData для локальной проверки Mini App.

Telegram открывает Mini App только по HTTPS, поэтому локально (http://localhost)
проверить авторизацию можно только с поддельной, но корректно подписанной
строкой initData. Скрипт собирает её ровно так же, как это делает Telegram,
и печатает готовый результат.

Использование:

    uv run python scripts/make_init_data.py 1066210990
    uv run python scripts/make_init_data.py 1066210990 --username boris --first-name Boris

Полученную строку можно:
  * подставить в mockTelegramEnv() на фронтенде (см. frontend/lib/telegram-dev.ts);
  * передать в запрос curl -H 'X-Telegram-Init-Data: <строка>' http://localhost:8000/me
"""

import argparse
import hashlib
import hmac
import json
import os
import time
from urllib.parse import urlencode

# Заглушка вместо Ed25519-подписи Telegram: SDK требует наличия поля,
# но проверяет его только на стороне Telegram, а не у нас.
FAKE_SIGNATURE = "dev" + "0" * 82


def build_init_data(
    token: str,
    user: dict[str, object],
    *,
    auth_date: int | None = None,
    start_param: str | None = None,
    chat: dict[str, object] | None = None,
    signature: str = FAKE_SIGNATURE,
) -> str:
    """Собирает initData с корректной HMAC-подписью (алгоритм Telegram).

    Поле `signature` (Ed25519) подписывает сам Telegram, его у нас нет —
    подставляем заглушку. Но в data-check-string оно входит, поэтому
    подпись `hash` считается уже с ним. На проверку hash это не влияет:
    бэкенд смотрит только на HMAC-SHA256 токена бота.
    """
    payload: dict[str, str] = {
        "user": json.dumps(user, separators=(",", ":"), ensure_ascii=False),
        "auth_date": str(auth_date if auth_date is not None else int(time.time())),
        "signature": signature,
    }
    if start_param:
        payload["start_param"] = start_param
    if chat:
        payload["chat"] = json.dumps(chat, separators=(",", ":"), ensure_ascii=False)

    data_check_string = "\n".join(
        f"{key}={value}" for key, value in sorted(payload.items())
    )
    secret_key = hmac.new(
        key=b"WebAppData", msg=token.encode(), digestmod=hashlib.sha256
    ).digest()
    signature = hmac.new(
        key=secret_key, msg=data_check_string.encode(), digestmod=hashlib.sha256
    ).hexdigest()

    payload["hash"] = signature
    return urlencode(payload)


def main() -> None:
    parser = argparse.ArgumentParser(description="Сгенерировать initData для Mini App")
    parser.add_argument("user_id", type=int, help="telegram id пользователя")
    parser.add_argument("--first-name", default="Dev", help="имя")
    parser.add_argument("--last-name", default="User", help="фамилия")
    parser.add_argument("--username", default="dev_user", help="username")
    parser.add_argument("--language-code", default="ru", help="язык")
    parser.add_argument("--start-param", default=None, help="start_param")
    parser.add_argument(
        "--token",
        default=None,
        help="токен бота (по умолчанию берётся из BOT_TOKEN)",
    )
    args = parser.parse_args()

    token = args.token or os.getenv("BOT_TOKEN", "")
    if not token:
        parser.error("Не найден токен бота: задайте BOT_TOKEN или --token")

    user: dict[str, object] = {
        "id": args.user_id,
        "first_name": args.first_name,
        "last_name": args.last_name,
        "username": args.username,
        "language_code": args.language_code,
    }

    init_data = build_init_data(token, user, start_param=args.start_param)
    print(init_data)
    print()
    print("Проверка:")
    print(f"  curl -H 'X-Telegram-Init-Data: {init_data}' http://localhost:8000/me")


if __name__ == "__main__":
    main()
