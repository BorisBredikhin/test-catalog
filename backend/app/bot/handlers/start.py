from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    WebAppInfo,
)

from app.config import settings

router = Router(name="start")


def webapp_keyboard() -> InlineKeyboardMarkup | None:
    """Клавиатура с кнопкой запуска Mini App (None, если URL не настроен)."""
    if not settings.webapp_url:
        return None

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Открыть каталог",
                    web_app=WebAppInfo(url=settings.webapp_url),
                )
            ]
        ]
    )


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    keyboard = webapp_keyboard()
    if keyboard is None:
        await message.answer("У меня есть товар")
        return

    await message.answer("Каталог товаров:", reply_markup=keyboard)
