from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.config import settings
from app.repositories.media_repository import MediaRepository
from app.schemas.media_asset import MediaAssetCreate


def _upload_root() -> Path:
    if settings.media_upload_dir:
        return Path(settings.media_upload_dir)
    return Path(__file__).resolve().parent.parent.parent / "data" / "uploads"


class MediaService:
    def __init__(self, session: Session) -> None:
        self.repo = MediaRepository(session)
        self.session = session

    def list_assets(self):
        return self.repo.list_all()

    def get(self, asset_id: int):
        row = self.repo.get(asset_id)
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Media asset not found"
            )
        return row

    async def create_from_upload(
        self,
        *,
        asset_type: str,
        title: str,
        alt_text: str | None,
        file: UploadFile,
    ):
        root = _upload_root()
        root.mkdir(parents=True, exist_ok=True)
        suffix = Path(file.filename or "upload").suffix or ".bin"
        safe_name = f"{uuid4().hex}{suffix}"
        dest = root / safe_name
        mime = file.content_type or "application/octet-stream"
        try:
            content = await file.read()
            dest.write_bytes(content)
        finally:
            await file.close()
        public_path = f"/uploads/{safe_name}"
        payload = MediaAssetCreate(
            asset_type=asset_type,
            title=title,
            file_path=public_path,
            mime_type=mime,
            alt_text=alt_text,
            thumbnail_path=None,
        )
        return self.repo.create(
            asset_type=payload.asset_type,
            title=payload.title,
            file_path=payload.file_path,
            mime_type=payload.mime_type,
            alt_text=payload.alt_text,
            thumbnail_path=payload.thumbnail_path,
        )

    def create_from_metadata(self, payload: MediaAssetCreate):
        return self.repo.create(
            asset_type=payload.asset_type,
            title=payload.title,
            file_path=payload.file_path,
            mime_type=payload.mime_type,
            alt_text=payload.alt_text,
            thumbnail_path=payload.thumbnail_path,
        )

    def delete(self, asset_id: int) -> None:
        row = self.get(asset_id)
        path = row.file_path
        if path.startswith("/uploads/"):
            disk = _upload_root() / Path(path).name
            if disk.is_file():
                disk.unlink()
        self.repo.delete(row)
