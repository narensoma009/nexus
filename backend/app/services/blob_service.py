import os
from pathlib import Path
from azure.storage.blob.aio import BlobServiceClient

from app.config import settings

_LOCAL_DIR = Path(os.getenv("LOCAL_BLOB_DIR", "./local_blobs"))


def _is_local() -> bool:
    return not settings.AZURE_STORAGE_CONNECTION_STRING


async def upload_blob(path: str, data: bytes) -> str:
    if _is_local():
        target = _LOCAL_DIR / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        return str(target)

    async with BlobServiceClient.from_connection_string(settings.AZURE_STORAGE_CONNECTION_STRING) as client:
        container = client.get_container_client(settings.AZURE_STORAGE_CONTAINER)
        try:
            await container.create_container()
        except Exception:
            pass
        await container.upload_blob(name=path, data=data, overwrite=True)
    return path


async def download_blob(path: str) -> bytes:
    if _is_local():
        target = _LOCAL_DIR / path
        return target.read_bytes()

    async with BlobServiceClient.from_connection_string(settings.AZURE_STORAGE_CONNECTION_STRING) as client:
        container = client.get_container_client(settings.AZURE_STORAGE_CONTAINER)
        downloader = await container.download_blob(path)
        return await downloader.readall()


async def delete_blob(path: str) -> bool:
    """Delete a blob. Returns True if removed, False if it didn't exist."""
    if _is_local():
        target = _LOCAL_DIR / path
        if target.exists():
            target.unlink()
            return True
        return False

    async with BlobServiceClient.from_connection_string(settings.AZURE_STORAGE_CONNECTION_STRING) as client:
        container = client.get_container_client(settings.AZURE_STORAGE_CONTAINER)
        try:
            await container.delete_blob(path)
            return True
        except Exception:
            return False
