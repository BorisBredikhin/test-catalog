from typing import Annotated

from aiogram.utils.web_app import WebAppUser
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.config import settings
from app.webapp_auth import telegram_user

router = APIRouter()


class TelegramUserProfile(BaseModel):
    """Профиль пользователя Telegram для отображения в Mini App."""

    id: int
    first_name: str
    last_name: str | None = None
    username: str | None = None
    language_code: str | None = None
    photo_url: str | None = None
    is_admin: bool = False

    @classmethod
    def from_aiogram(cls, user: WebAppUser, *, is_admin: bool = False) -> "TelegramUserProfile":
        return cls(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
            language_code=user.language_code,
            photo_url=user.photo_url,
            is_admin=is_admin,
        )


@router.get("/me", response_model=TelegramUserProfile)
async def me(
    user: Annotated[WebAppUser, Depends(telegram_user)],
) -> TelegramUserProfile:
    """Профиль текущего пользователя Mini App (initData проверяется)."""
    return TelegramUserProfile.from_aiogram(user, is_admin=user.id in settings.admin_id_set)
