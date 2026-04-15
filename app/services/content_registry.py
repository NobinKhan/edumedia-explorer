from __future__ import annotations

from typing import Literal, NotRequired, TypedDict

ContentType = Literal["text", "image", "audio", "video", "youtube"]


class ContentItem(TypedDict):
    id: str
    type: ContentType
    title: str
    description: str
    body_text: NotRequired[str]
    asset_url: NotRequired[str]
    embed_url: NotRequired[str]
    thumbnail_url: NotRequired[str]


CONTENT_REGISTRY: dict[str, ContentItem] = {
    "interactive-learning": {
        "id": "interactive-learning",
        "type": "text",
        "title": "Interactive Learning",
        "description": "Sample text content for the demo.",
        "body_text": (
            "Interactive learning works best when you can explore concepts in context. "
            "In this demo, highlighted terms and media cards open a single reusable modal."
        ),
    },
    "visual-example": {
        "id": "visual-example",
        "type": "image",
        "title": "Visual Example",
        "description": "A locally served image asset.",
        "asset_url": "/static/media/sample-image.jpg",
        "thumbnail_url": "/static/media/sample-image.jpg",
    },
    "spoken-note": {
        "id": "spoken-note",
        "type": "audio",
        "title": "Spoken Note",
        "description": "A short locally served audio clip.",
        "asset_url": "/static/media/sample-audio.mp3",
    },
    "demo-video": {
        "id": "demo-video",
        "type": "video",
        "title": "Local Demo Video",
        "description": "A short locally served video clip.",
        "asset_url": "/static/media/sample-video.mp4",
        "thumbnail_url": "/static/media/sample-image.jpg",
    },
    "external-reference": {
        "id": "external-reference",
        "type": "youtube",
        "title": "YouTube Reference",
        "description": "Embedded YouTube video with a fallback link.",
        "embed_url": "https://www.youtube-nocookie.com/embed/dQw4w9WgXcQ",
        "asset_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "thumbnail_url": "/static/media/sample-image.jpg",
    },
}


def get_content(content_id: str) -> ContentItem | None:
    return CONTENT_REGISTRY.get(content_id)
