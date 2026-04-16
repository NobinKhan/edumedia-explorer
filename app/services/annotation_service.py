from __future__ import annotations

from sqlalchemy.orm import Session

from app.errors import bad_request, not_found
from app.repositories.annotation_repository import AnnotationRepository
from app.repositories.media_repository import MediaRepository
from app.repositories.page_repository import PageRepository
from app.schemas.annotation import AnnotationCreate, AnnotationUpdate
from app.schemas.common import ANNOTATION_TYPES_FROZEN
from app.services.page_service import PageService
from app.services.render_service import (
    offsets_use_single_text_node,
    plain_text_length,
    slice_plain_text,
)
from app.util.youtube import is_plausible_youtube_url


class AnnotationService:
    def __init__(self, session: Session) -> None:
        self.repo = AnnotationRepository(session)
        self.pages = PageRepository(session)
        self.media = MediaRepository(session)
        self.session = session

    def _validate_payload(
        self,
        *,
        page_raw: str,
        annotation_type: str,
        trigger_text: str,
        start_offset: int,
        end_offset: int,
        body_text: str | None,
        media_asset_id: int | None,
        youtube_url: str | None,
        link_label: str | None,
    ) -> None:
        if annotation_type not in ANNOTATION_TYPES_FROZEN:
            raise bad_request("Invalid annotation_type")
        if end_offset <= start_offset:
            raise bad_request(
                "end_offset must be greater than start_offset for an annotation span."
            )
        plain_len = plain_text_length(page_raw)
        if start_offset < 0 or end_offset > plain_len:
            raise bad_request("Annotation offsets are out of range for the page plain text length.")
        try:
            segment = slice_plain_text(page_raw, start_offset, end_offset)
        except ValueError as exc:
            raise bad_request(str(exc)) from exc
        if not (trigger_text or "").strip():
            raise bad_request("trigger_text is required for anchored annotations.")
        if segment != trigger_text:
            raise bad_request("trigger_text must match the plain text slice at the given offsets.")
        if not offsets_use_single_text_node(page_raw, start_offset, end_offset):
            raise bad_request(
                "Annotation must be confined to a single text node in the HTML body "
                "(selection cannot cross element boundaries)."
            )

        if annotation_type == "text":
            if not (body_text and body_text.strip()):
                raise bad_request("text annotations require body_text")
        elif annotation_type in {"image", "audio", "video"}:
            if media_asset_id is None:
                raise bad_request(f"{annotation_type} annotations require media_asset_id")
            asset = self.media.get(media_asset_id)
            if asset is None:
                raise bad_request("media_asset_id not found")
            if asset.asset_type != annotation_type:
                raise bad_request("Media asset type does not match annotation type")
        elif annotation_type == "youtube":
            if not youtube_url or not is_plausible_youtube_url(youtube_url):
                raise bad_request("youtube annotations require a plausible youtube_url")
        elif annotation_type == "link_note":
            if not (link_label or "").strip() and not (body_text or "").strip():
                raise bad_request("link_note annotations require link_label and/or body_text")

    def list_for_page(self, page_id: int):
        PageService(self.session).get(page_id)
        return self.repo.list_for_page(page_id)

    def get(self, annotation_id: int):
        row = self.repo.get(annotation_id)
        if row is None:
            raise not_found("Annotation not found")
        return row

    def create(self, page_id: int, payload: AnnotationCreate):
        page = PageService(self.session).get(page_id)
        self._validate_payload(
            page_raw=page.raw_content,
            annotation_type=payload.annotation_type,
            trigger_text=payload.trigger_text,
            start_offset=payload.start_offset,
            end_offset=payload.end_offset,
            body_text=payload.body_text,
            media_asset_id=payload.media_asset_id,
            youtube_url=payload.youtube_url,
            link_label=payload.link_label,
        )
        row = self.repo.create(
            subject_page_id=page_id,
            annotation_type=payload.annotation_type,
            trigger_text=payload.trigger_text,
            start_offset=payload.start_offset,
            end_offset=payload.end_offset,
            display_mode=payload.display_mode,
            title=payload.title,
            body_text=payload.body_text,
            media_asset_id=payload.media_asset_id,
            youtube_url=payload.youtube_url,
            link_label=payload.link_label,
        )
        return row

    def update(self, annotation_id: int, payload: AnnotationUpdate):
        row = self.get(annotation_id)
        page = PageService(self.session).get(row.subject_page_id, load_annotations=False)
        data = payload.model_dump(exclude_unset=True)
        merged_type = data.get("annotation_type", row.annotation_type)
        merged_trigger = data.get("trigger_text", row.trigger_text)
        merged_start = data.get("start_offset", row.start_offset)
        merged_end = data.get("end_offset", row.end_offset)
        merged_body = data.get("body_text", row.body_text)
        merged_media = data.get("media_asset_id", row.media_asset_id)
        merged_youtube = data.get("youtube_url", row.youtube_url)
        merged_link = data.get("link_label", row.link_label)
        self._validate_payload(
            page_raw=page.raw_content,
            annotation_type=merged_type,
            trigger_text=merged_trigger,
            start_offset=merged_start,
            end_offset=merged_end,
            body_text=merged_body,
            media_asset_id=merged_media,
            youtube_url=merged_youtube,
            link_label=merged_link,
        )
        return self.repo.apply_patch(row, data)

    def delete(self, annotation_id: int) -> None:
        row = self.get(annotation_id)
        self.repo.delete(row)
