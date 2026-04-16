from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, File, Form, UploadFile

from app.dependencies import DbSession
from app.schemas.media_asset import MediaAssetCreate, MediaAssetRead
from app.services.media_service import MediaService

router = APIRouter(prefix="/media-assets", tags=["media-assets"])


@router.get("/", response_model=list[MediaAssetRead])
def list_media_assets(session: DbSession) -> list[MediaAssetRead]:
    return MediaService(session).list_assets()


@router.post("/", response_model=MediaAssetRead, status_code=201)
def create_media_asset_json(payload: MediaAssetCreate, session: DbSession) -> MediaAssetRead:
    """Create a media asset from metadata (e.g. seeded `/static/...` paths)."""
    return MediaService(session).create_from_metadata(payload)


@router.post("/upload", response_model=MediaAssetRead, status_code=201)
async def upload_media_asset(
    file: Annotated[UploadFile, File()],
    session: DbSession,
    asset_type: str = Form(),
    title: str = Form(),
    alt_text: str | None = Form(None),
) -> MediaAssetRead:
    return await MediaService(session).create_from_upload(
        asset_type=asset_type, title=title, alt_text=alt_text, file=file
    )


@router.get("/{asset_id}", response_model=MediaAssetRead)
def read_media_asset(asset_id: int, session: DbSession) -> MediaAssetRead:
    return MediaService(session).get(asset_id)


@router.delete("/{asset_id}", status_code=204)
def delete_media_asset(asset_id: int, session: DbSession) -> None:
    MediaService(session).delete(asset_id)
