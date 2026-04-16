from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.annotation import Annotation


class SubjectPage(Base, TimestampMixin):
    __tablename__ = "subject_pages"
    __table_args__ = (UniqueConstraint("slug", name="uq_subject_page_slug"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE"), nullable=False, index=True
    )
    sub_category_id: Mapped[int] = mapped_column(
        ForeignKey("sub_categories.id", ondelete="CASCADE"), nullable=False, index=True
    )
    sub_sub_category_id: Mapped[int] = mapped_column(
        ForeignKey("sub_sub_categories.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False)
    summary: Mapped[str] = mapped_column(Text(), nullable=False, default="")
    raw_content: Mapped[str] = mapped_column(Text(), nullable=False, default="")
    rendered_content: Mapped[str] = mapped_column(Text(), nullable=False, default="")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="draft", index=True)

    annotations: Mapped[list[Annotation]] = relationship(
        "Annotation",
        back_populates="subject_page",
        cascade="all, delete-orphan",
        order_by="Annotation.id",
    )
