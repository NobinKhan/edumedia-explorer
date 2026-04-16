from __future__ import annotations

from urllib.parse import urlparse

_ALLOWED = frozenset(
    {
        "youtube.com",
        "www.youtube.com",
        "m.youtube.com",
        "youtu.be",
        "www.youtu.be",
        "www.youtube-nocookie.com",
        "youtube-nocookie.com",
    }
)


def is_plausible_youtube_url(url: str) -> bool:
    parsed = urlparse(url.strip())
    if parsed.scheme not in ("http", "https"):
        return False
    host = (parsed.hostname or "").lower()
    return host in _ALLOWED
