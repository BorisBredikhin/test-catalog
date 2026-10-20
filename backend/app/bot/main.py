import logging

from aiogram import Bot, Dispatcher
from aiogram.types import ErrorEvent

from app.bot.handlers.admin import denied_router
from app.bot.handlers.admin import router as admin_router
from app.bot.handlers.start import router as start_router
from app.bot.middlewares import DbSessionMiddleware
from app.config import settings

logger = logging.getLogger(__name__)


def create_bot() -> Bot:
    return Bot(token=settings.bot_token)


def create_dispatcher() -> Dispatcher:
    dp = Dispatcher()
    dp.update.middleware(DbSessionMiddleware())
    dp.include_router(admin_router)
    dp.include_router(denied_router)
    dp.include_router(start_router)

    @dp.errors()
    async def on_error(event: ErrorEvent) -> bool:
        logger.error("Ошибка в боте: %s", event.exception, exc_info=event.exception)
        return True

    return dp
