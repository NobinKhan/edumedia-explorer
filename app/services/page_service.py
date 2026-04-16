from __future__ import annotations

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.errors import conflict, not_found
from app.repositories.page_repository import PageRepository
from app.schemas.subject_page import SubjectPageCreate, SubjectPageUpdate
from app.services.hierarchy import assert_subject_hierarchy
from app.services.render_service import build_interactive_html


class PageService:
    def __init__(self, session: Session) -> None:
        self.repo = PageRepository(session)
        self.session = session

    def list_pages(
        self,
        *,
        category_id: int | None = None,
        sub_category_id: int | None = None,
        sub_sub_category_id: int | None = None,
        status: str | None = None,
        search: str | None = None,
    ):
        return self.repo.list_filtered(
            category_id=category_id,
            sub_category_id=sub_category_id,
            sub_sub_category_id=sub_sub_category_id,
            status=status,
            search=search,
        )

    def get(self, page_id: int, *, load_annotations: bool = False):
        row = self.repo.get(page_id, load_annotations=load_annotations)
        if row is None:
            raise not_found("Subject page not found")
        return row

    def get_by_slug(self, slug: str, *, load_annotations: bool = False):
        row = self.repo.get_by_slug(slug, load_annotations=load_annotations)
        if row is None:
            raise not_found("Subject page not found")
        return row

    def create(self, payload: SubjectPageCreate):
        assert_subject_hierarchy(
            self.session,
            category_id=payload.category_id,
            sub_category_id=payload.sub_category_id,
            sub_sub_category_id=payload.sub_sub_category_id,
        )
        if self.repo.get_by_slug(payload.slug):
            raise conflict("Subject page slug already exists.")
        rendered = build_interactive_html(payload.raw_content, [])
        try:
            return self.repo.create(
                category_id=payload.category_id,
                sub_category_id=payload.sub_category_id,
                sub_sub_category_id=payload.sub_sub_category_id,
                title=payload.title,
                slug=payload.slug,
                summary=payload.summary,
                raw_content=payload.raw_content,
                rendered_content=rendered,
                status=payload.status,
            )
        except IntegrityError as exc:
            self.session.rollback()
            raise conflict("Could not create subject page (slug conflict).") from exc

    def update(self, page_id: int, payload: SubjectPageUpdate):
        row = self.get(page_id, load_annotations=True)
        cat = payload.category_id if payload.category_id is not None else row.category_id
        sub = (
            payload.sub_category_id if payload.sub_category_id is not None else row.sub_category_id
        )
        subsub = (
            payload.sub_sub_category_id
            if payload.sub_sub_category_id is not None
            else row.sub_sub_category_id
        )
        assert_subject_hierarchy(
            self.session, category_id=cat, sub_category_id=sub, sub_sub_category_id=subsub
        )
        new_slug = payload.slug if payload.slug is not None else row.slug
        existing = self.repo.get_by_slug(new_slug)
        if existing is not None and existing.id != row.id:
            raise conflict("Subject page slug already exists.")
        rendered_kw: object = ...
        if payload.raw_content is not None:
            rendered_kw = build_interactive_html(payload.raw_content, list(row.annotations))
        try:
            return self.repo.update(
                row,
                category_id=payload.category_id if payload.category_id is not None else ...,
                sub_category_id=payload.sub_category_id
                if payload.sub_category_id is not None
                else ...,
                sub_sub_category_id=payload.sub_sub_category_id
                if payload.sub_sub_category_id is not None
                else ...,
                title=payload.title if payload.title is not None else ...,
                slug=payload.slug if payload.slug is not None else ...,
                summary=payload.summary if payload.summary is not None else ...,
                raw_content=payload.raw_content if payload.raw_content is not None else ...,
                rendered_content=rendered_kw,
                status=payload.status if payload.status is not None else ...,
            )
        except IntegrityError as exc:
            self.session.rollback()
            raise conflict("Could not update subject page (slug conflict).") from exc

    def delete(self, page_id: int) -> None:
        row = self.get(page_id)
        self.repo.delete(row)

    def publish(self, page_id: int):
        row = self.get(page_id, load_annotations=True)
        row.rendered_content = build_interactive_html(row.raw_content, list(row.annotations))
        row.status = "published"
        self.session.flush()
        return row

    def preview(self, page_id: int, raw_override: str | None = None):
        row = self.get(page_id, load_annotations=True)
        raw = raw_override if raw_override is not None else row.raw_content
        rendered = build_interactive_html(raw, list(row.annotations))
        return {"rendered_content": rendered}

    def rendered_payload(self, page_id: int):
        row = self.get(page_id)
        return {"rendered_content": row.rendered_content}
