from __future__ import annotations

from fastapi import APIRouter

from app.dependencies import DbSession
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate
from app.services.category_service import CategoryService

router = APIRouter(tags=["categories"])


@router.get("/", response_model=list[CategoryRead])
def list_categories(session: DbSession) -> list[CategoryRead]:
    return CategoryService(session).list_categories()


@router.post("/", response_model=CategoryRead, status_code=201)
def create_category(payload: CategoryCreate, session: DbSession) -> CategoryRead:
    return CategoryService(session).create(payload)


@router.get("/{category_id}", response_model=CategoryRead)
def read_category(category_id: int, session: DbSession) -> CategoryRead:
    return CategoryService(session).get(category_id)


@router.patch("/{category_id}", response_model=CategoryRead)
def update_category(category_id: int, payload: CategoryUpdate, session: DbSession) -> CategoryRead:
    return CategoryService(session).update(category_id, payload)


@router.delete("/{category_id}", status_code=204)
def delete_category(category_id: int, session: DbSession) -> None:
    CategoryService(session).delete(category_id)
