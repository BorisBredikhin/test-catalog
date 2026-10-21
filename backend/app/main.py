import asyncio
import logging
import os
from contextlib import asynccontextmanager, suppress
from typing import Annotated

from aiogram import Bot
from aiogram.types import MenuButtonWebApp, WebAppInfo
from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.main import create_bot, create_dispatcher
from app.config import settings
from app.db import get_session
from app.product_router import router as product_router
from app.storage import ensure_bucket
from app.webapp_router import router as webapp_router

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)-8s %(name)s %(message)s",
)

logger = logging.getLogger(__name__)


def _log_polling_done(task: asyncio.Task[None]) -> None:
    if task.cancelled():
        return
    exc = task.exception()
    if exc is not None:
        logger.error("Polling бота завершился с ошибкой", exc_info=exc)


async def _setup_menu_button(bot: Bot) -> None:
    """Кнопка меню чата открывает Mini App (как и кнопка в сообщении бота)."""
    if not settings.webapp_url:
        return

    try:
        await bot.set_chat_menu_button(
            menu_button=MenuButtonWebApp(
                text="Каталог",
                web_app=WebAppInfo(url=settings.webapp_url),
            )
        )
        logger.info("Кнопка меню чата открывает Mini App %s", settings.webapp_url)
    except Exception:
        logger.exception("Не удалось настроить кнопку меню чата")


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await ensure_bucket()
    except Exception:
        logger.exception("Не удалось создать бакет MinIO")

    bot = None
    dispatcher = None
    polling_task = None
    if settings.bot_token:
        try:
            bot = create_bot()
            dispatcher = create_dispatcher()
        except Exception:
            logger.exception("Не удалось создать бота — он не будет запущен")
            bot = None
            dispatcher = None
        if dispatcher is not None:
            polling_task = asyncio.create_task(
                dispatcher.start_polling(bot, handle_signals=False),
                name="bot-polling",
            )
            polling_task.add_done_callback(_log_polling_done)
            logger.info("Telegram-бот запущен")
            await _setup_menu_button(bot)
    else:
        logger.warning("BOT_TOKEN не задан — Telegram-бот не запущен")

    yield

    if dispatcher is not None and polling_task is not None:
        with suppress(RuntimeError):  # polling ещё не стартовал / уже остановлен
            await dispatcher.stop_polling()
        try:
            await asyncio.wait_for(polling_task, timeout=15)
        except TimeoutError:
            logger.warning("Polling бота не остановился за 15 с — задача отменена")
        except Exception:
            logger.exception("Polling бота завершился с ошибкой")


app = FastAPI(title="test-catalog", lifespan=lifespan)


@app.get("/health")
async def health(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> dict[str, str]:
    await session.execute(text("SELECT 1"))
    return {"status": "ok"}


app.include_router(product_router, prefix="/product")
app.include_router(webapp_router)
