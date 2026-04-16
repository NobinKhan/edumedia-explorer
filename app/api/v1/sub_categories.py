from __future__ import annotations

from fastapi import APIRouter, Query

from app.dependencies import DbSession
from app.schemas.sub_category import SubCategoryCreate, SubCategoryRead, SubCategoryUpdate
from app.services.sub_category_service import SubCategoryService

router = APIRouter(tags=["sub-categories"])


@router.get("/", response_model=list[SubCategoryRead])
def list_sub_categories(
    session: DbSession,
    category_id: int | None = Query(default=None),
) -> list[SubCategoryRead]:
    return SubCategoryService(session).list(category_id=category_id)


@router.post("/", response_model=SubCategoryRead, status_code=201)
def create_sub_category(payload: SubCategoryCreate, session: DbSession) -> SubCategoryRead:
    return SubCategoryService(session).create(payload)


@router.get("/{sub_category_id}", response_model=SubCategoryRead)
def read_sub_category(sub_category_id: int, session: DbSession) -> SubCategoryRead:
    return SubCategoryService(session).get(sub_category_id)


@router.patch("/{sub_category_id}", response_model=SubCategoryRead)
def update_sub_category(
    sub_category_id: int, payload: SubCategoryUpdate, session: DbSession
) -> SubCategoryRead:
    return SubCategoryService(session).update(sub_category_id, payload)


@router.delete("/{sub_category_id}", status_code=204)
def delete_sub_category(sub_category_id: int, session: DbSession) -> None:
    SubCategoryService(session).delete(sub_category_id)
