from __future__ import annotations

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.errors import bad_request, conflict, not_found
from app.repositories.category_repository import CategoryRepository
from app.repositories.sub_category_repository import SubCategoryRepository
from app.schemas.sub_category import SubCategoryCreate, SubCategoryUpdate


class SubCategoryService:
    def __init__(self, session: Session) -> None:
        self.repo = SubCategoryRepository(session)
        self.categories = CategoryRepository(session)
        self.session = session

    def list(self, *, category_id: int | None = None):
        return self.repo.list_filtered(category_id=category_id)

    def get(self, sub_category_id: int):
        row = self.repo.get(sub_category_id)
        if row is None:
            raise not_found("Sub-category not found")
        return row

    def create(self, payload: SubCategoryCreate):
        if self.categories.get(payload.category_id) is None:
            raise bad_request("Category not found")
        if self.repo.get_by_slug(payload.category_id, payload.slug):
            raise conflict("Sub-category slug already exists for this category.")
        try:
            return self.repo.create(
                category_id=payload.category_id,
                name=payload.name,
                slug=payload.slug,
                description=payload.description,
            )
        except IntegrityError as exc:
            self.session.rollback()
            raise conflict("Could not create sub-category (slug conflict).") from exc

    def update(self, sub_category_id: int, payload: SubCategoryUpdate):
        row = self.get(sub_category_id)
        target_cat = payload.category_id if payload.category_id is not None else row.category_id
        if self.categories.get(target_cat) is None:
            raise bad_request("Category not found")
        new_slug = payload.slug if payload.slug is not None else row.slug
        existing = self.repo.get_by_slug(target_cat, new_slug)
        if existing is not None and existing.id != row.id:
            raise conflict("Sub-category slug already exists for this category.")
        try:
            return self.repo.update(
                row,
                category_id=payload.category_id,
                name=payload.name,
                slug=payload.slug,
                description=payload.description,
            )
        except IntegrityError as exc:
            self.session.rollback()
            raise conflict("Could not update sub-category (slug conflict).") from exc

    def delete(self, sub_category_id: int) -> None:
        row = self.get(sub_category_id)
        self.repo.delete(row)
