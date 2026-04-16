from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.sub_sub_category import SubSubCategory


class SubSubCategoryRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_filtered(self, *, sub_category_id: int | None = None) -> list[SubSubCategory]:
        stmt = select(SubSubCategory).order_by(SubSubCategory.id)
        if sub_category_id is not None:
            stmt = stmt.where(SubSubCategory.sub_category_id == sub_category_id)
        return list(self.session.scalars(stmt))

    def get(self, sub_sub_category_id: int) -> SubSubCategory | None:
        return self.session.get(SubSubCategory, sub_sub_category_id)

    def get_by_slug(self, sub_category_id: int, slug: str) -> SubSubCategory | None:
        return self.session.scalar(
            select(SubSubCategory).where(
                SubSubCategory.sub_category_id == sub_category_id,
                SubSubCategory.slug == slug,
            )
        )

    def create(
        self, *, sub_category_id: int, name: str, slug: str, description: str
    ) -> SubSubCategory:
        row = SubSubCategory(
            sub_category_id=sub_category_id, name=name, slug=slug, description=description
        )
        self.session.add(row)
        self.session.flush()
        return row

    def update(
        self,
        row: SubSubCategory,
        *,
        sub_category_id: int | None,
        name: str | None,
        slug: str | None,
        description: str | None,
    ) -> SubSubCategory:
        if sub_category_id is not None:
            row.sub_category_id = sub_category_id
        if name is not None:
            row.name = name
        if slug is not None:
            row.slug = slug
        if description is not None:
            row.description = description
        self.session.flush()
        return row

    def delete(self, row: SubSubCategory) -> None:
        self.session.delete(row)
        self.session.flush()
