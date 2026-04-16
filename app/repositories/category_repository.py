from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.category import Category


class CategoryRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_all(self) -> list[Category]:
        return list(self.session.scalars(select(Category).order_by(Category.id)))

    def get(self, category_id: int) -> Category | None:
        return self.session.get(Category, category_id)

    def get_by_slug(self, slug: str) -> Category | None:
        return self.session.scalar(select(Category).where(Category.slug == slug))

    def create(self, *, name: str, slug: str, description: str) -> Category:
        row = Category(name=name, slug=slug, description=description)
        self.session.add(row)
        self.session.flush()
        return row

    def update(
        self, row: Category, *, name: str | None, slug: str | None, description: str | None
    ) -> Category:
        if name is not None:
            row.name = name
        if slug is not None:
            row.slug = slug
        if description is not None:
            row.description = description
        self.session.flush()
        return row

    def delete(self, row: Category) -> None:
        self.session.delete(row)
        self.session.flush()
