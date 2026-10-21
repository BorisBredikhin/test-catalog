import logging

from aiogram.filters import BaseFilter
from aiogram.types import Message

from app.config import settings

logger = logging.getLogger(__name__)


class IsAdmin(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        user = message.from_user
        logger.info(
            "Проверка прав пользователя %s (%s): %s",
            user,
            user.id if user else None,
            settings.admin_id_set,
        )
        return user is not None and user.id in settings.admin_id_set
