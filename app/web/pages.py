from __future__ import annotations

import json
from urllib.parse import parse_qs, urlparse

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.dependencies import DbSession
from app.models.media_asset import MediaAsset
from app.models.subject_page import SubjectPage
from app.services.page_service import PageService

router = APIRouter(tags=["web"])
templates = Jinja2Templates(directory="app/templates")


def _youtube_embed(url: str) -> str:
    parsed = urlparse(url.strip())
    host = (parsed.hostname or "").lower()
    q = parse_qs(parsed.query)
    if host in {"youtu.be", "www.youtu.be"}:
        vid = (parsed.path or "").strip("/").split("/")[0]
        if vid:
            return f"https://www.youtube-nocookie.com/embed/{vid}"
    if "youtube.com" in host:
        vid = (q.get("v") or [None])[0]
        if vid:
            return f"https://www.youtube-nocookie.com/embed/{vid}"
        path_parts = [p for p in (parsed.path or "").split("/") if p]
        if "embed" in path_parts:
            idx = path_parts.index("embed")
            if idx + 1 < len(path_parts):
                return f"https://www.youtube-nocookie.com/embed/{path_parts[idx + 1]}"
    return ""


def _annotation_modal_items(session: Session, page: SubjectPage) -> list[dict[str, object]]:
    items: list[dict[str, object]] = []
    for ann in page.annotations:
        item: dict[str, object] = {
            "id": str(ann.id),
            "type": ann.annotation_type,
            "title": ann.title or ann.trigger_text,
            "description": (ann.body_text or "")[:280],
        }
        if ann.annotation_type == "text":
            item["body_text"] = ann.body_text or ""
        if ann.annotation_type in {"image", "audio", "video"} and ann.media_asset_id:
            ma = session.get(MediaAsset, ann.media_asset_id)
            if ma:
                item["asset_url"] = ma.file_path
        if ann.annotation_type == "youtube" and ann.youtube_url:
            item["asset_url"] = ann.youtube_url
            item["embed_url"] = _youtube_embed(ann.youtube_url)
        if ann.annotation_type == "link_note":
            body = ann.body_text or ""
            item["body_text"] = body
            item["link_label"] = ann.link_label or "Open link"
            if body.startswith(("http://", "https://")):
                item["asset_url"] = body
        items.append(item)
    return items


@router.get("/pages/{slug}", response_class=HTMLResponse)
def public_subject_page(slug: str, request: Request, session: DbSession) -> HTMLResponse:
    page = PageService(session).get_by_slug(slug, load_annotations=True)
    if page.status != "published":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page not found")
    annotations_json = json.dumps(_annotation_modal_items(session, page))
    return templates.TemplateResponse(
        request,
        "page_view.html",
        {
            "request": request,
            "page": page,
            "annotations_json": annotations_json,
        },
    )
