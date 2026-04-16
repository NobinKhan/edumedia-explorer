from __future__ import annotations

from fastapi import APIRouter

from app.dependencies import DbSession
from app.schemas.annotation import AnnotationRead, AnnotationUpdate
from app.services.annotation_service import AnnotationService

router = APIRouter(prefix="/annotations", tags=["annotations"])


@router.get("/{annotation_id}", response_model=AnnotationRead)
def read_annotation(annotation_id: int, session: DbSession) -> AnnotationRead:
    return AnnotationService(session).get(annotation_id)


@router.patch("/{annotation_id}", response_model=AnnotationRead)
def update_annotation(
    annotation_id: int, payload: AnnotationUpdate, session: DbSession
) -> AnnotationRead:
    return AnnotationService(session).update(annotation_id, payload)


@router.delete("/{annotation_id}", status_code=204)
def delete_annotation(annotation_id: int, session: DbSession) -> None:
    AnnotationService(session).delete(annotation_id)
