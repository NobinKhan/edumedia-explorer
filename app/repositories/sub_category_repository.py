from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.sub_category import SubCategory


class SubCategoryRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_filtered(self, *, category_id: int | None = None) -> list[SubCategory]:
        stmt = select(SubCategory).order_by(SubCategory.id)
        if category_id is not None:
            stmt = stmt.where(SubCategory.category_id == category_id)
        return list(self.session.scalars(stmt))

    def get(self, sub_category_id: int) -> SubCategory | None:
        return self.session.get(SubCategory, sub_category_id)

    def get_by_slug(self, category_id: int, slug: str) -> SubCategory | None:
        return self.session.scalar(
            select(SubCategory).where(
                SubCategory.category_id == category_id,
                SubCategory.slug == slug,
            )
        )

    def create(self, *, category_id: int, name: str, slug: str, description: str) -> SubCategory:
        row = SubCategory(category_id=category_id, name=name, slug=slug, description=description)
        self.session.add(row)
        self.session.flush()
        return row

    def update(
        self,
        row: SubCategory,
        *,
        category_id: int | None,
        name: str | None,
        slug: str | None,
        description: str | None,
    ) -> SubCategory:
        if category_id is not None:
            row.category_id = category_id
        if name is not None:
            row.name = name
        if slug is not None:
            row.slug = slug
        if description is not None:
            row.description = description
        self.session.flush()
        return row

    def delete(self, row: SubCategory) -> None:
        self.session.delete(row)
        self.session.flush()
