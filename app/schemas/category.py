from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.common import assert_slug


class CategoryBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    slug: str = Field(min_length=1, max_length=255)
    description: str = ""

    @field_validator("slug")
    @classmethod
    def slug_ok(cls, v: str) -> str:
        return assert_slug(v)


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    slug: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None

    @field_validator("slug")
    @classmethod
    def slug_ok(cls, v: str | None) -> str | None:
        if v is None:
            return v
        return assert_slug(v)


class CategoryRead(CategoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
