from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.common import ANNOTATION_TYPES_FROZEN


class AnnotationBase(BaseModel):
    annotation_type: str
    trigger_text: str = Field(default="", max_length=512)
    start_offset: int = Field(ge=0)
    end_offset: int = Field(ge=0)
    display_mode: str = "modal"
    title: str = Field(default="", max_length=255)
    body_text: str | None = None
    media_asset_id: int | None = None
    youtube_url: str | None = Field(default=None, max_length=512)
    link_label: str | None = Field(default=None, max_length=255)

    @field_validator("annotation_type")
    @classmethod
    def type_ok(cls, v: str) -> str:
        if v not in ANNOTATION_TYPES_FROZEN:
            raise ValueError(f"annotation_type must be one of {sorted(ANNOTATION_TYPES_FROZEN)}")
        return v


class AnnotationCreate(AnnotationBase):
    pass


class AnnotationUpdate(BaseModel):
    annotation_type: str | None = None
    trigger_text: str | None = Field(default=None, max_length=512)
    start_offset: int | None = Field(default=None, ge=0)
    end_offset: int | None = Field(default=None, ge=0)
    display_mode: str | None = None
    title: str | None = Field(default=None, max_length=255)
    body_text: str | None = None
    media_asset_id: int | None = None
    youtube_url: str | None = Field(default=None, max_length=512)
    link_label: str | None = Field(default=None, max_length=255)

    @field_validator("annotation_type")
    @classmethod
    def type_ok(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if v not in ANNOTATION_TYPES_FROZEN:
            raise ValueError(f"annotation_type must be one of {sorted(ANNOTATION_TYPES_FROZEN)}")
        return v


class AnnotationRead(AnnotationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    subject_page_id: int
    created_at: datetime
    updated_at: datetime
