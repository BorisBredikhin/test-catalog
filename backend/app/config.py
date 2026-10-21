from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://catalog:catalog@localhost:5432/catalog"

    # Telegram-бот
    bot_token: str = ""
    admin_ids: str = ""  # telegram id админов через запятую

    # Telegram Mini App
    webapp_url: str = ""  # публичный HTTPS-URL фронтенда (Telegram требует https)
    webapp_dev: bool = False  # не проверять подпись initData (локальная разработка)

    # MinIO
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "catalog"
    minio_public_url: str = "http://localhost:9000"
    minio_secure: bool = False

    @property
    def admin_id_set(self) -> set[int]:
        ids: set[int] = set()
        for raw in self.admin_ids.split(","):
            raw = raw.strip()
            if not raw:
                continue
            try:
                ids.add(int(raw))
            except ValueError:
                continue
        return ids


settings = Settings()
