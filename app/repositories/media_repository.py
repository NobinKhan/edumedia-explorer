from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.media_asset import MediaAsset


class MediaRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_all(self) -> list[MediaAsset]:
        return list(self.session.scalars(select(MediaAsset).order_by(MediaAsset.id)))

    def get(self, asset_id: int) -> MediaAsset | None:
        return self.session.get(MediaAsset, asset_id)

    def create(
        self,
        *,
        asset_type: str,
        title: str,
        file_path: str,
        mime_type: str,
        alt_text: str | None,
        thumbnail_path: str | None,
    ) -> MediaAsset:
        row = MediaAsset(
            asset_type=asset_type,
            title=title,
            file_path=file_path,
            mime_type=mime_type,
            alt_text=alt_text,
            thumbnail_path=thumbnail_path,
        )
        self.session.add(row)
        self.session.flush()
        return row

    def delete(self, row: MediaAsset) -> None:
        self.session.delete(row)
        self.session.flush()
