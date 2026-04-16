from __future__ import annotations

import logging
from collections.abc import Callable

from starlette.concurrency import run_in_threadpool
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from user_agents import parse as ua_parse

from app.db import SessionLocal
from app.models.request_log import RequestLog

logger = logging.getLogger(__name__)

_SKIP_PREFIXES = (
    "/static",
    "/uploads",
    "/tracker",
    "/openapi.json",
    "/docs",
    "/redoc",
)
_SKIP_PATHS = frozenset({"/healthz", "/favicon.ico"})


def _should_skip_path(path: str) -> bool:
    if path in _SKIP_PATHS:
        return True
    return any(path.startswith(p) for p in _SKIP_PREFIXES)


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()[:255]
    if request.client:
        return request.client.host[:255]
    return ""


def _route_path(request: Request) -> str:
    route = request.scope.get("route")
    if route is not None:
        p = getattr(route, "path", None)
        if isinstance(p, str) and p:
            return p[:2048]
    return request.url.path[:2048]


def _parse_user_agent(ua: str | None) -> tuple[str, str, str]:
    if not ua:
        return "unknown", "unknown", "unknown"
    parsed = ua_parse(ua[:2000])
    if parsed.is_mobile:
        kind = "mobile"
    elif parsed.is_tablet:
        kind = "tablet"
    elif parsed.is_pc:
        kind = "desktop"
    else:
        kind = "unknown"
    os_f = (parsed.os.family or "unknown")[:64]
    browser = (parsed.browser.family or "unknown")[:64]
    return kind, os_f, browser


def _log_request_sync(
    *,
    method: str,
    path: str,
    status_code: int,
    client_ip: str,
    user_agent: str,
    device_kind: str,
    os_family: str,
    browser_family: str,
) -> None:
    import app.config as cfg

    settings = cfg.settings
    secret = settings.tracker_secret
    if not secret or not str(secret).strip():
        return

    session = SessionLocal()
    try:
        row = RequestLog(
            method=method[:16],
            path=path[:2048],
            status_code=status_code,
            client_ip=client_ip[:255],
            user_agent=user_agent[:512],
            device_kind=device_kind[:32],
            os_family=os_family[:64],
            browser_family=browser_family[:64],
        )
        session.add(row)
        session.commit()

        from sqlalchemy import delete, func, select

        max_rows = settings.tracker_max_rows
        total = session.scalar(select(func.count()).select_from(RequestLog))
        if total and total > max_rows:
            excess = total - max_rows
            old_ids = session.scalars(
                select(RequestLog.id).order_by(RequestLog.created_at.asc()).limit(excess)
            ).all()
            if old_ids:
                session.execute(delete(RequestLog).where(RequestLog.id.in_(old_ids)))
            session.commit()
    except Exception:
        logger.exception("request log insert failed")
        session.rollback()
    finally:
        session.close()


class RequestLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        path = request.url.path
        if request.method == "OPTIONS" or _should_skip_path(path):
            return response

        import app.config as cfg

        if not cfg.settings.tracker_secret or not str(cfg.settings.tracker_secret).strip():
            return response

        ua_header = request.headers.get("user-agent")
        device_kind, os_family, browser_family = _parse_user_agent(ua_header)
        method = request.method
        route_path = _route_path(request)
        ip = _client_ip(request)
        ua_trunc = (ua_header or "")[:512]
        status = response.status_code

        await run_in_threadpool(
            _log_request_sync,
            method=method,
            path=route_path,
            status_code=status,
            client_ip=ip,
            user_agent=ua_trunc,
            device_kind=device_kind,
            os_family=os_family,
            browser_family=browser_family,
        )
        return response
