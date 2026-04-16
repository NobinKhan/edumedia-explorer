from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.common import MEDIA_TYPES_FROZEN


class MediaAssetBase(BaseModel):
    asset_type: str
    title: str = Field(min_length=1, max_length=255)
    file_path: str = Field(min_length=1, max_length=512)
    mime_type: str = Field(min_length=1, max_length=128)
    alt_text: str | None = Field(default=None, max_length=512)
    thumbnail_path: str | None = Field(default=None, max_length=512)

    @field_validator("asset_type")
    @classmethod
    def asset_type_ok(cls, v: str) -> str:
        if v not in MEDIA_TYPES_FROZEN:
            raise ValueError(f"asset_type must be one of {sorted(MEDIA_TYPES_FROZEN)}")
        return v


class MediaAssetCreate(MediaAssetBase):
    pass


class MediaAssetRead(MediaAssetBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
