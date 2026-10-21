import asyncio
import io
import json
import uuid

from app.config import settings
from minio import Minio


def _client() -> Minio:
    return Minio(
        endpoint=settings.minio_endpoint,
        access_key=settings.minio_access_key,
        secret_key=settings.minio_secret_key,
        secure=settings.minio_secure,
    )


def _public_read_policy(bucket: str) -> str:
    return json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": ["*"]},
                    "Action": ["s3:GetObject"],
                    "Resource": [f"arn:aws:s3:::{bucket}/*"],
                }
            ],
        }
    )


async def ensure_bucket() -> None:
    def _ensure() -> None:
        client = _client()
        if not client.bucket_exists(settings.minio_bucket):
            client.make_bucket(settings.minio_bucket)
        client.set_bucket_policy(
            settings.minio_bucket, _public_read_policy(settings.minio_bucket)
        )

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
