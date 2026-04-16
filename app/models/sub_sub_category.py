from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.sub_category import SubCategory


class SubSubCategory(Base, TimestampMixin):
    __tablename__ = "sub_sub_categories"
    __table_args__ = (
        UniqueConstraint("sub_category_id", "slug", name="uq_sub_sub_slug_per_sub_cat"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    sub_category_id: Mapped[int] = mapped_column(
        ForeignKey("sub_categories.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text(), nullable=False, default="")

    sub_category: Mapped[SubCategory] = relationship(
        "SubCategory", back_populates="sub_sub_categories"
    )
