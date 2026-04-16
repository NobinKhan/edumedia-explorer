from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.category import Category
    from app.models.sub_sub_category import SubSubCategory


class SubCategory(Base, TimestampMixin):
    __tablename__ = "sub_categories"
    __table_args__ = (UniqueConstraint("category_id", "slug", name="uq_sub_category_slug_per_cat"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text(), nullable=False, default="")

    category: Mapped[Category] = relationship("Category", back_populates="sub_categories")
    sub_sub_categories: Mapped[list[SubSubCategory]] = relationship(
        "SubSubCategory", back_populates="sub_category", cascade="all, delete-orphan"
    )
