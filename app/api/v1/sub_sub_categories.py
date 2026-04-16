from __future__ import annotations

from fastapi import APIRouter, Query

from app.dependencies import DbSession
from app.schemas.sub_sub_category import (
    SubSubCategoryCreate,
    SubSubCategoryRead,
    SubSubCategoryUpdate,
)
from app.services.sub_sub_category_service import SubSubCategoryService

router = APIRouter(tags=["sub-sub-categories"])


@router.get("/", response_model=list[SubSubCategoryRead])
def list_sub_sub_categories(
    session: DbSession,
    sub_category_id: int | None = Query(default=None),
) -> list[SubSubCategoryRead]:
    return SubSubCategoryService(session).list(sub_category_id=sub_category_id)


@router.post("/", response_model=SubSubCategoryRead, status_code=201)
def create_sub_sub_category(
    payload: SubSubCategoryCreate, session: DbSession
) -> SubSubCategoryRead:
    return SubSubCategoryService(session).create(payload)


@router.get("/{sub_sub_category_id}", response_model=SubSubCategoryRead)
def read_sub_sub_category(sub_sub_category_id: int, session: DbSession) -> SubSubCategoryRead:
    return SubSubCategoryService(session).get(sub_sub_category_id)


@router.patch("/{sub_sub_category_id}", response_model=SubSubCategoryRead)
def update_sub_sub_category(
    sub_sub_category_id: int, payload: SubSubCategoryUpdate, session: DbSession
) -> SubSubCategoryRead:
    return SubSubCategoryService(session).update(sub_sub_category_id, payload)


@router.delete("/{sub_sub_category_id}", status_code=204)
def delete_sub_sub_category(sub_sub_category_id: int, session: DbSession) -> None:
    SubSubCategoryService(session).delete(sub_sub_category_id)
