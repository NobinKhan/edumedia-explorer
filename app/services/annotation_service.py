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
from bs4 import BeautifulSoup, NavigableString


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

    def _reanchor_offsets(
        self, *, page_raw: str, trigger_text: str, preferred_start: int | None
    ) -> tuple[int, int] | None:
        # Try exact trigger first; fall back to trimmed trigger if needed.
        candidates = [trigger_text or ""]
        trimmed = (trigger_text or "").strip()
        if trimmed and trimmed != candidates[0]:
            candidates.append(trimmed)
        candidates = [c for c in candidates if c]
        if not candidates:
            return None
        soup = BeautifulSoup(page_raw or "", "html.parser")
        for tag in soup(["script", "style"]):
            tag.decompose()
        mapping: list[tuple[NavigableString, int]] = []
        for node in soup.descendants:
            if (
                isinstance(node, NavigableString)
                and node.parent
                and node.parent.name
                and node.parent.name not in ("script", "style")
            ):
                chunk = str(node)
                for i in range(len(chunk)):
                    mapping.append((node, i))
        if not mapping:
            return None
        chars = []
        for n, i in mapping:
            chunk = str(n)
            chars.append(chunk[i : i + 1])
        plain = "".join(chars)
        if not plain:
            return None
        for trigger in candidates:
            positions: list[int] = []
            idx = plain.find(trigger)
            while idx != -1:
                positions.append(idx)
                idx = plain.find(trigger, idx + 1)
            if not positions:
                continue
            best = positions[0]
            if preferred_start is not None:
                best_dist = abs(best - preferred_start)
                for p in positions:
                    d = abs(p - preferred_start)
                    if d < best_dist:
                        best, best_dist = p, d
            start, end = best, best + len(trigger)
            if not offsets_use_single_text_node(page_raw, start, end):
                # Try other occurrences that satisfy single-text-node constraint.
                for p in positions:
                    s, e = p, p + len(trigger)
                    if offsets_use_single_text_node(page_raw, s, e):
                        start, end = s, e
                        break
            return (start, end)
        return None

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
        # If client offsets are stale/mismatched, re-anchor using backend mapping.
        plain_len = plain_text_length(page.raw_content)
        start_offset = payload.start_offset
        end_offset = payload.end_offset
        try:
            segment = slice_plain_text(page.raw_content, start_offset, end_offset)
        except ValueError:
            segment = None
        if (
            start_offset < 0
            or end_offset > plain_len
            or (segment is not None and segment != payload.trigger_text)
        ):
            anchored = self._reanchor_offsets(
                page_raw=page.raw_content,
                trigger_text=payload.trigger_text,
                preferred_start=start_offset if start_offset >= 0 else None,
            )
            if anchored is not None:
                start_offset, end_offset = anchored
        self._validate_payload(
            page_raw=page.raw_content,
            annotation_type=payload.annotation_type,
            trigger_text=payload.trigger_text,
            start_offset=start_offset,
            end_offset=end_offset,
            body_text=payload.body_text,
            media_asset_id=payload.media_asset_id,
            youtube_url=payload.youtube_url,
            link_label=payload.link_label,
        )
        row = self.repo.create(
            subject_page_id=page_id,
            annotation_type=payload.annotation_type,
            trigger_text=payload.trigger_text,
            start_offset=start_offset,
            end_offset=end_offset,
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
