from aiogram.filters import BaseFilter
from aiogram.types import Message

from app.config import settings


class IsAdmin(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        user = message.from_user
        return user is not None and user.id in settings.admin_id_set
