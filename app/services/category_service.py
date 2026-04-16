from __future__ import annotations

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.errors import conflict, not_found
from app.repositories.category_repository import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryUpdate


class CategoryService:
    def __init__(self, session: Session) -> None:
        self.repo = CategoryRepository(session)
        self.session = session

    def list_categories(self):
        return self.repo.list_all()

    def get(self, category_id: int):
        row = self.repo.get(category_id)
        if row is None:
            raise not_found("Category not found")
        return row

    def create(self, payload: CategoryCreate):
        if self.repo.get_by_slug(payload.slug):
            raise conflict("Category slug already exists.")
        try:
            return self.repo.create(
                name=payload.name, slug=payload.slug, description=payload.description
            )
        except IntegrityError as exc:
            self.session.rollback()
            raise conflict("Could not create category (slug conflict).") from exc

    def update(self, category_id: int, payload: CategoryUpdate):
        row = self.get(category_id)
        if payload.slug is not None and payload.slug != row.slug:
            if self.repo.get_by_slug(payload.slug):
                raise conflict("Category slug already exists.")
        try:
            return self.repo.update(
                row,
                name=payload.name,
                slug=payload.slug,
                description=payload.description,
            )
        except IntegrityError as exc:
            self.session.rollback()
            raise conflict("Could not update category (slug conflict).") from exc

    def delete(self, category_id: int) -> None:
        row = self.get(category_id)
        self.repo.delete(row)
