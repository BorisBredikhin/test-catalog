import logging

from aiogram import F, Router
from aiogram.dispatcher.event.bases import SkipHandler
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.filters import IsAdmin
from app.bot.states import AddProduct
from app.models import Product
from app.storage import upload_product_photo

logger = logging.getLogger(__name__)

router = Router(name="admin")
router.message.filter(IsAdmin())

# Ответ для не-админов; подключается после router в диспетчере
denied_router = Router(name="admin-denied")


@router.message(Command("add"))
async def cmd_add(message: Message, state: FSMContext) -> None:
    await state.set_state(AddProduct.photo)
    await message.answer(
        "Отправьте фото товара с названием в подписи к фото.\nОтменить — /cancel."
    )


@router.message(Command("cancel"), StateFilter(AddProduct.photo))
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Добавление отменено.")


@router.message(StateFilter(AddProduct.photo), F.photo)
async def add_product_photo(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
) -> None:
    caption = (message.caption or "").strip()
    if not caption:
        await message.answer(
            "В подписи нет названия товара. Отправьте фото ещё раз с подписью."
        )
        return

    if message.photo is None or len(message.photo) != 1:
        await message.answer("Должно быть приложено ровно одно фото")
        return

    assert message.bot, "Бот недоступен"

    photo = message.photo[-1]
    buf = await message.bot.download(photo.file_id)
    if buf is None:
        await message.answer("Не удалось скачать фото. Отправьте его ещё раз.")
        return

    url = await upload_product_photo(buf.read())
    session.add(Product(name=caption, photo_url=url))
    await session.commit()
    await state.clear()
    logger.info("Добавлен товар %r (photo: %s)", caption, url)
    await message.answer(f"✅ Товар «{caption}» добавлен в каталог.")


@router.message(StateFilter(AddProduct.photo))
async def add_product_wrong(message: Message) -> None:
    if message.text and message.text.startswith("/"):
        raise SkipHandler
    await message.answer("Нужно фото с подписью — названием товара.")


@denied_router.message(Command("add"))
async def add_denied(message: Message) -> None:
    await message.answer("Команда доступна только администратору.")
