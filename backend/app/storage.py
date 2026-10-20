import asyncio
import io
import uuid

from minio import Minio

from app.config import settings


def _client() -> Minio:
    return Minio(
        endpoint=settings.minio_endpoint,
        access_key=settings.minio_access_key,
        secret_key=settings.minio_secret_key,
        secure=settings.minio_secure,
    )


async def ensure_bucket() -> None:
    def _ensure() -> None:
        client = _client()
        if not client.bucket_exists(settings.minio_bucket):
            client.make_bucket(settings.minio_bucket)

    await asyncio.to_thread(_ensure)


async def upload_product_photo(data: bytes, content_type: str = "image/jpeg") -> str:
    ext = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}.get(
        content_type, "jpg"
    )
    object_name = f"products/{uuid.uuid4().hex}.{ext}"

    def _upload() -> None:
        _client().put_object(
            settings.minio_bucket,
            object_name,
            io.BytesIO(data),
            length=len(data),
            content_type=content_type,
        )

    await asyncio.to_thread(_upload)
    base = settings.minio_public_url.rstrip("/")
    return f"{base}/{settings.minio_bucket}/{object_name}"
