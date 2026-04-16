from __future__ import annotations

import re
from typing import Literal

SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

AnnotationType = Literal["text", "image", "audio", "video", "youtube", "link_note"]
PageStatus = Literal["draft", "published"]
MediaAssetType = Literal["image", "audio", "video"]


def assert_slug(value: str) -> str:
    if not SLUG_RE.fullmatch(value):
        raise ValueError(
            "Slug must be lowercase letters, digits, and hyphens only, "
            "without leading or trailing hyphens."
        )
    return value


ANNOTATION_TYPES_FROZEN = frozenset({"text", "image", "audio", "video", "youtube", "link_note"})
PAGE_STATUSES_FROZEN = frozenset({"draft", "published"})
MEDIA_TYPES_FROZEN = frozenset({"image", "audio", "video"})
