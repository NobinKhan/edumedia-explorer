from __future__ import annotations

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.errors import bad_request, conflict, not_found
from app.repositories.sub_category_repository import SubCategoryRepository
from app.repositories.sub_sub_category_repository import SubSubCategoryRepository
from app.schemas.sub_sub_category import SubSubCategoryCreate, SubSubCategoryUpdate


class SubSubCategoryService:
    def __init__(self, session: Session) -> None:
        self.repo = SubSubCategoryRepository(session)
        self.sub_categories = SubCategoryRepository(session)
        self.session = session

    def list(self, *, sub_category_id: int | None = None):
        return self.repo.list_filtered(sub_category_id=sub_category_id)

    def get(self, sub_sub_category_id: int):
        row = self.repo.get(sub_sub_category_id)
        if row is None:
            raise not_found("Sub-sub-category not found")
        return row

    def create(self, payload: SubSubCategoryCreate):
        if self.sub_categories.get(payload.sub_category_id) is None:
            raise bad_request("Sub-category not found")
        if self.repo.get_by_slug(payload.sub_category_id, payload.slug):
            raise conflict("Sub-sub-category slug already exists for this sub-category.")
        try:
            return self.repo.create(
                sub_category_id=payload.sub_category_id,
                name=payload.name,
                slug=payload.slug,
                description=payload.description,
            )
        except IntegrityError as exc:
            self.session.rollback()
            raise conflict("Could not create sub-sub-category (slug conflict).") from exc

    def update(self, sub_sub_category_id: int, payload: SubSubCategoryUpdate):
        row = self.get(sub_sub_category_id)
        target_sub = (
            payload.sub_category_id if payload.sub_category_id is not None else row.sub_category_id
        )
        if self.sub_categories.get(target_sub) is None:
            raise bad_request("Sub-category not found")
        new_slug = payload.slug if payload.slug is not None else row.slug
        existing = self.repo.get_by_slug(target_sub, new_slug)
        if existing is not None and existing.id != row.id:
            raise conflict("Sub-sub-category slug already exists for this sub-category.")
        try:
            return self.repo.update(
                row,
                sub_category_id=payload.sub_category_id,
                name=payload.name,
                slug=payload.slug,
                description=payload.description,
            )
        except IntegrityError as exc:
            self.session.rollback()
            raise conflict("Could not update sub-sub-category (slug conflict).") from exc

    def delete(self, sub_sub_category_id: int) -> None:
        row = self.get(sub_sub_category_id)
        self.repo.delete(row)
