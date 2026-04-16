from __future__ import annotations

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.subject_page import SubjectPage


class PageRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_filtered(
        self,
        *,
        category_id: int | None = None,
        sub_category_id: int | None = None,
        sub_sub_category_id: int | None = None,
        status: str | None = None,
        search: str | None = None,
        load_annotations: bool = False,
    ) -> list[SubjectPage]:
        stmt = select(SubjectPage).order_by(SubjectPage.id)
        if category_id is not None:
            stmt = stmt.where(SubjectPage.category_id == category_id)
        if sub_category_id is not None:
            stmt = stmt.where(SubjectPage.sub_category_id == sub_category_id)
        if sub_sub_category_id is not None:
            stmt = stmt.where(SubjectPage.sub_sub_category_id == sub_sub_category_id)
        if status is not None:
            stmt = stmt.where(SubjectPage.status == status)
        if search:
            stmt = stmt.where(
                or_(
                    SubjectPage.title.contains(search),
                    SubjectPage.summary.contains(search),
                )
            )
        if load_annotations:
            stmt = stmt.options(selectinload(SubjectPage.annotations))
        return list(self.session.scalars(stmt))

    def get(self, page_id: int, *, load_annotations: bool = False) -> SubjectPage | None:
        stmt = select(SubjectPage).where(SubjectPage.id == page_id)
        if load_annotations:
            stmt = stmt.options(selectinload(SubjectPage.annotations))
        return self.session.scalar(stmt)

    def get_by_slug(self, slug: str, *, load_annotations: bool = False) -> SubjectPage | None:
        stmt = select(SubjectPage).where(SubjectPage.slug == slug)
        if load_annotations:
            stmt = stmt.options(selectinload(SubjectPage.annotations))
        return self.session.scalar(stmt)

    def create(
        self,
        *,
        category_id: int,
        sub_category_id: int,
        sub_sub_category_id: int,
        title: str,
        slug: str,
        summary: str,
        raw_content: str,
        rendered_content: str,
        status: str,
    ) -> SubjectPage:
        row = SubjectPage(
            category_id=category_id,
            sub_category_id=sub_category_id,
            sub_sub_category_id=sub_sub_category_id,
            title=title,
            slug=slug,
            summary=summary,
            raw_content=raw_content,
            rendered_content=rendered_content,
            status=status,
        )
        self.session.add(row)
        self.session.flush()
        return row

    def update(
        self,
        row: SubjectPage,
        *,
        category_id: int | None | object = ...,
        sub_category_id: int | None | object = ...,
        sub_sub_category_id: int | None | object = ...,
        title: str | None | object = ...,
        slug: str | None | object = ...,
        summary: str | None | object = ...,
        raw_content: str | None | object = ...,
        rendered_content: str | object = ...,
        status: str | None | object = ...,
    ) -> SubjectPage:
        if category_id is not ...:
            row.category_id = category_id  # type: ignore[assignment]
        if sub_category_id is not ...:
            row.sub_category_id = sub_category_id  # type: ignore[assignment]
        if sub_sub_category_id is not ...:
            row.sub_sub_category_id = sub_sub_category_id  # type: ignore[assignment]
        if title is not ...:
            row.title = title  # type: ignore[assignment]
        if slug is not ...:
            row.slug = slug  # type: ignore[assignment]
        if summary is not ...:
            row.summary = summary  # type: ignore[assignment]
        if raw_content is not ...:
            row.raw_content = raw_content  # type: ignore[assignment]
        if rendered_content is not ...:
            row.rendered_content = rendered_content  # type: ignore[assignment]
        if status is not ...:
            row.status = status  # type: ignore[assignment]
        self.session.flush()
        return row

    def delete(self, row: SubjectPage) -> None:
        self.session.delete(row)
        self.session.flush()
