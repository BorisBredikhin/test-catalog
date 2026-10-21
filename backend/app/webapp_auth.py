"""Аутентификация Telegram Mini App по подписи initData.

Mini App передаёт боту строку `initData`, подписанную HMAC-SHA256 ключом,
который Telegram выводит из токена бота. Проверять подпись обязательно:
данные, которые Mini App отдаёт в браузере, доверять нельзя.
"""

import logging
from typing import Annotated

from aiogram.utils.web_app import WebAppUser, safe_parse_webapp_init_data
from fastapi import Header, HTTPException, status

from app.config import settings

logger = logging.getLogger(__name__)

INIT_DATA_HEADER = "X-Telegram-Init-Data"

# Заглушка для локальной разработки: Mini App ещё не открыт в Telegram,
# а initData сгенерировать нечем.
DEV_USER = WebAppUser(
    id=0,
    first_name="Dev",
    last_name="User",
    username="dev_user",
    language_code="ru",
)


def parse_init_data(init_data: str) -> WebAppUser:
    """Проверяет подпись initData и возвращает пользователя Telegram."""
    if not settings.bot_token:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="BOT_TOKEN не задан — авторизация Mini App недоступна",
        )

    try:
        parsed = safe_parse_webapp_init_data(settings.bot_token, init_data)
    except ValueError as exc:
        logger.warning("InitData не прошла проверку подписи: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Некорректные данные Mini App",
        ) from exc

    if parsed.user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="В initData нет пользователя",
        )

    return parsed.user


async def telegram_user(
    init_data: Annotated[str | None, Header(alias=INIT_DATA_HEADER)] = None,
) -> WebAppUser:
    """Зависимость FastAPI: пользователь Telegram по заголовку X-Telegram-Init-Data."""
    if init_data:
        return parse_init_data(init_data)

    if settings.webapp_dev:
        logger.warning("InitData не передан — используется dev-пользователь")
        return DEV_USER

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Заголовок X-Telegram-Init-Data обязателен",
    )
