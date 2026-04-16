from __future__ import annotations

import secrets
from typing import TYPE_CHECKING

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from starlette.requests import Request
from starlette.responses import Response

if TYPE_CHECKING:
    pass

TRACKER_HEADER = "x-tracker-secret"
TRACKER_COOKIE = "tracker_session"
COOKIE_MAX_AGE_SECONDS = 604800  # 7 days
COOKIE_SALT = "edumedia-tracker"


def _settings():
    import app.config as cfg

    return cfg.settings


def tracker_enabled() -> bool:
    s = _settings().tracker_secret
    return bool(s and str(s).strip())


def _serializer() -> URLSafeTimedSerializer:
    secret = _settings().tracker_secret or ""
    return URLSafeTimedSerializer(secret_key=secret, salt=COOKIE_SALT)


def verify_secret_header(request: Request) -> bool:
    if not tracker_enabled():
        return False
    expected = _settings().tracker_secret or ""
    hdr = request.headers.get(TRACKER_HEADER)
    if not hdr:
        return False
    return secrets.compare_digest(hdr, expected)


def verify_cookie(request: Request) -> bool:
    if not tracker_enabled():
        return False
    raw = request.cookies.get(TRACKER_COOKIE)
    if not raw:
        return False
    ser = _serializer()
    try:
        ser.loads(raw, max_age=COOKIE_MAX_AGE_SECONDS)
        return True
    except (BadSignature, SignatureExpired):
        return False


def is_tracker_authenticated(request: Request) -> bool:
    return verify_secret_header(request) or verify_cookie(request)


def set_tracker_cookie(response: Response) -> None:
    token = _serializer().dumps({"ok": True})
    response.set_cookie(
        TRACKER_COOKIE,
        token,
        max_age=COOKIE_MAX_AGE_SECONDS,
        httponly=True,
        samesite="lax",
        secure=False,
        path="/tracker",
    )


def clear_tracker_cookie(response: Response) -> None:
    response.delete_cookie(TRACKER_COOKIE, path="/tracker")
