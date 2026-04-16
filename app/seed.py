from __future__ import annotations

from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from app.models.annotation import Annotation
from app.models.category import Category
from app.models.media_asset import MediaAsset
from app.models.sub_category import SubCategory
from app.models.sub_sub_category import SubSubCategory
from app.models.subject_page import SubjectPage
from app.services.render_service import build_interactive_html


def _plain_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()
    parts: list[str] = []
    for node in soup.descendants:
        if getattr(node, "name", None) in {"script", "style"}:
            continue
        if isinstance(node, str):
            parts.append(node)
    return "".join(parts)


def seed(session: Session) -> None:
    """Create a small demo dataset.

    Idempotent-ish: if a category with slug 'science' exists, do nothing.
    """
    existing = session.query(Category).filter(Category.slug == "science").first()
    if existing is not None:
        return

    cat = Category(name="Science", slug="science", description="Science topics")
    session.add(cat)
    session.flush()

    sub = SubCategory(
        category_id=cat.id,
        name="Biology",
        slug="biology",
        description="Living systems",
    )
    session.add(sub)
    session.flush()

    leaf = SubSubCategory(
        sub_category_id=sub.id,
        name="Plants",
        slug="plants",
        description="Plant biology",
    )
    session.add(leaf)
    session.flush()

    img = MediaAsset(
        asset_type="image",
        title="Sample image",
        file_path="/static/media/sample-image.jpg",
        mime_type="image/jpeg",
        alt_text="Sample image",
        thumbnail_path="/static/media/sample-image.jpg",
    )
    session.add(img)
    session.flush()

    raw = (
        "<p><b>Photosynthesis</b> is how plants convert light into energy. "
        "The process occurs in chloroplasts.</p>"
        "<p>Select a term like chloroplasts in the editor to attach a note.</p>"
    )
    page = SubjectPage(
        category_id=cat.id,
        sub_category_id=sub.id,
        sub_sub_category_id=leaf.id,
        title="Photosynthesis",
        slug="photosynthesis",
        summary="An overview of how plants make energy.",
        raw_content=raw,
        rendered_content="",
        status="draft",
    )
    session.add(page)
    session.flush()

    # Note: offsets computed against the plain text derived from raw HTML.
    trigger = "chloroplasts"
    plain = _plain_text(raw)
    start = plain.find(trigger)
    if start < 0:
        # Should never happen; keep seed non-fatal.
        return
    ann = Annotation(
        subject_page_id=page.id,
        annotation_type="image",
        trigger_text=trigger,
        start_offset=start,
        end_offset=start + len(trigger),
        display_mode="modal",
        title="Chloroplasts",
        body_text="Organelles where photosynthesis occurs.",
        media_asset_id=img.id,
        youtube_url=None,
        link_label=None,
    )
    session.add(ann)
    session.flush()

    # Publish (render with annotation spans)
    page.rendered_content = build_interactive_html(page.raw_content, [ann])
    page.status = "published"
    session.flush()
