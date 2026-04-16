from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.annotation import Annotation


class AnnotationRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_for_page(self, page_id: int) -> list[Annotation]:
        return list(
            self.session.scalars(
                select(Annotation)
                .where(Annotation.subject_page_id == page_id)
                .order_by(Annotation.id)
            )
        )

    def get(self, annotation_id: int) -> Annotation | None:
        return self.session.get(Annotation, annotation_id)

    def create(
        self,
        *,
        subject_page_id: int,
        annotation_type: str,
        trigger_text: str,
        start_offset: int,
        end_offset: int,
        display_mode: str,
        title: str,
        body_text: str | None,
        media_asset_id: int | None,
        youtube_url: str | None,
        link_label: str | None,
    ) -> Annotation:
        row = Annotation(
            subject_page_id=subject_page_id,
            annotation_type=annotation_type,
            trigger_text=trigger_text,
            start_offset=start_offset,
            end_offset=end_offset,
            display_mode=display_mode,
            title=title,
            body_text=body_text,
            media_asset_id=media_asset_id,
            youtube_url=youtube_url,
            link_label=link_label,
        )
        self.session.add(row)
        self.session.flush()
        return row

    def apply_patch(self, row: Annotation, patch: dict[str, object]) -> Annotation:
        for key, value in patch.items():
            setattr(row, key, value)
        self.session.flush()
        return row

    def delete(self, row: Annotation) -> None:
        self.session.delete(row)
        self.session.flush()
