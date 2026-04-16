from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.media_asset import MediaAsset
    from app.models.subject_page import SubjectPage


class Annotation(Base, TimestampMixin):
    __tablename__ = "annotations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    subject_page_id: Mapped[int] = mapped_column(
        ForeignKey("subject_pages.id", ondelete="CASCADE"), nullable=False, index=True
    )
    annotation_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    trigger_text: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    start_offset: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    end_offset: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    display_mode: Mapped[str] = mapped_column(String(32), nullable=False, default="modal")
    title: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    body_text: Mapped[str | None] = mapped_column(Text(), nullable=True)
    media_asset_id: Mapped[int | None] = mapped_column(
        ForeignKey("media_assets.id", ondelete="SET NULL"), nullable=True
    )
    youtube_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    link_label: Mapped[str | None] = mapped_column(String(255), nullable=True)

    subject_page: Mapped[SubjectPage] = relationship("SubjectPage", back_populates="annotations")
    media_asset: Mapped[MediaAsset | None] = relationship("MediaAsset")
