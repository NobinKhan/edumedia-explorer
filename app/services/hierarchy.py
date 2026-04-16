from __future__ import annotations

from sqlalchemy.orm import Session

from app.errors import bad_request
from app.models.sub_category import SubCategory
from app.models.sub_sub_category import SubSubCategory


def assert_subject_hierarchy(
    session: Session,
    *,
    category_id: int,
    sub_category_id: int,
    sub_sub_category_id: int,
) -> None:
    sub = session.get(SubCategory, sub_category_id)
    if sub is None or sub.category_id != category_id:
        raise bad_request(
            "sub_category_id must reference a sub-category under the given category_id."
        )
    sub_sub = session.get(SubSubCategory, sub_sub_category_id)
    if sub_sub is None or sub_sub.sub_category_id != sub_category_id:
        raise bad_request(
            "sub_sub_category_id must reference a sub-sub-category under the given sub_category_id."
        )
