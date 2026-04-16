from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.common import PAGE_STATUSES_FROZEN, assert_slug


class SubjectPageBase(BaseModel):
    category_id: int
    sub_category_id: int
    sub_sub_category_id: int
    title: str = Field(min_length=1, max_length=255)
    slug: str = Field(min_length=1, max_length=255)
    summary: str = ""
    raw_content: str = ""
    status: str = "draft"

    @field_validator("slug")
    @classmethod
    def slug_ok(cls, v: str) -> str:
        return assert_slug(v)

    @field_validator("status")
    @classmethod
    def status_ok(cls, v: str) -> str:
        if v not in PAGE_STATUSES_FROZEN:
            raise ValueError("status must be draft or published")
        return v


class SubjectPageCreate(SubjectPageBase):
    pass


class SubjectPageUpdate(BaseModel):
    category_id: int | None = None
    sub_category_id: int | None = None
    sub_sub_category_id: int | None = None
    title: str | None = Field(default=None, min_length=1, max_length=255)
    slug: str | None = Field(default=None, min_length=1, max_length=255)
    summary: str | None = None
    raw_content: str | None = None
    status: str | None = None

    @field_validator("slug")
    @classmethod
    def slug_ok(cls, v: str | None) -> str | None:
        if v is None:
            return v
        return assert_slug(v)

    @field_validator("status")
    @classmethod
    def status_ok(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if v not in PAGE_STATUSES_FROZEN:
            raise ValueError("status must be draft or published")
        return v


class SubjectPageRead(SubjectPageBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    rendered_content: str
    created_at: datetime
    updated_at: datetime


class SubjectPagePreviewRequest(BaseModel):
    raw_content: str | None = None


class RenderedBody(BaseModel):
    rendered_content: str
