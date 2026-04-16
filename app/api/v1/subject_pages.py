from __future__ import annotations

from fastapi import APIRouter, Query

from app.dependencies import DbSession
from app.schemas.annotation import AnnotationCreate, AnnotationRead
from app.schemas.subject_page import (
    RenderedBody,
    SubjectPageCreate,
    SubjectPagePreviewRequest,
    SubjectPageRead,
    SubjectPageUpdate,
)
from app.services.annotation_service import AnnotationService
from app.services.page_service import PageService

router = APIRouter(tags=["subject-pages"])


@router.get("/", response_model=list[SubjectPageRead])
def list_subject_pages(
    session: DbSession,
    category_id: int | None = Query(default=None),
    sub_category_id: int | None = Query(default=None),
    sub_sub_category_id: int | None = Query(default=None),
    status: str | None = Query(default=None),
    search: str | None = Query(default=None),
) -> list[SubjectPageRead]:
    return PageService(session).list_pages(
        category_id=category_id,
        sub_category_id=sub_category_id,
        sub_sub_category_id=sub_sub_category_id,
        status=status,
        search=search,
    )


@router.post("/", response_model=SubjectPageRead, status_code=201)
def create_subject_page(payload: SubjectPageCreate, session: DbSession) -> SubjectPageRead:
    return PageService(session).create(payload)


@router.get("/{page_id}", response_model=SubjectPageRead)
def read_subject_page(page_id: int, session: DbSession) -> SubjectPageRead:
    return PageService(session).get(page_id)


@router.patch("/{page_id}", response_model=SubjectPageRead)
def update_subject_page(
    page_id: int, payload: SubjectPageUpdate, session: DbSession
) -> SubjectPageRead:
    return PageService(session).update(page_id, payload)


@router.delete("/{page_id}", status_code=204)
def delete_subject_page(page_id: int, session: DbSession) -> None:
    PageService(session).delete(page_id)


@router.post("/{page_id}/publish", response_model=SubjectPageRead)
def publish_subject_page(page_id: int, session: DbSession) -> SubjectPageRead:
    return PageService(session).publish(page_id)


@router.post("/{page_id}/preview", response_model=RenderedBody)
def preview_subject_page(
    page_id: int, payload: SubjectPagePreviewRequest, session: DbSession
) -> RenderedBody:
    data = PageService(session).preview(page_id, raw_override=payload.raw_content)
    return RenderedBody(**data)


@router.get("/{page_id}/rendered", response_model=RenderedBody)
def read_rendered_subject_page(page_id: int, session: DbSession) -> RenderedBody:
    return RenderedBody(**PageService(session).rendered_payload(page_id))


@router.get("/{page_id}/annotations", response_model=list[AnnotationRead])
def list_annotations(page_id: int, session: DbSession) -> list[AnnotationRead]:
    return AnnotationService(session).list_for_page(page_id)


@router.post("/{page_id}/annotations", response_model=AnnotationRead, status_code=201)
def create_annotation(
    page_id: int, payload: AnnotationCreate, session: DbSession
) -> AnnotationRead:
    return AnnotationService(session).create(page_id, payload)
