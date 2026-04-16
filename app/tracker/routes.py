from __future__ import annotations

import math
import secrets
from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, select
from sqlalchemy.orm import Session

import app.config as app_config
from app.db import get_session
from app.models.request_log import RequestLog
from app.tracker.auth import (
    clear_tracker_cookie,
    is_tracker_authenticated,
    set_tracker_cookie,
    tracker_enabled,
)
from app.tracker.data_reset import reset_app_data_preserve_request_logs

SessionDep = Annotated[Session, Depends(get_session)]

router = APIRouter(prefix="/tracker", tags=["tracker"], include_in_schema=False)
templates = Jinja2Templates(directory="app/templates")

PAGE_SIZE = 50


def _not_enabled() -> None:
    if not tracker_enabled():
        raise HTTPException(status_code=404, detail="Not found")


@router.get("", response_class=HTMLResponse, include_in_schema=False, response_model=None)
def tracker_home(request: Request) -> HTMLResponse | RedirectResponse:
    _not_enabled()
    if is_tracker_authenticated(request):
        return RedirectResponse(url="/tracker/dashboard", status_code=302)
    return templates.TemplateResponse(
        request,
        "tracker/login.html",
        {
            "request": request,
            "error": None,
            "title": "Usage tracker",
        },
    )


@router.post("/login", response_class=HTMLResponse, include_in_schema=False, response_model=None)
def tracker_login(
    request: Request,
    secret: Annotated[str, Form()],
) -> HTMLResponse | RedirectResponse:
    _not_enabled()
    expected = app_config.settings.tracker_secret or ""
    if not secrets.compare_digest(secret.strip(), expected.strip()):
        return templates.TemplateResponse(
            request,
            "tracker/login.html",
            {
                "request": request,
                "error": "Invalid secret.",
                "title": "Usage tracker",
            },
            status_code=401,
        )
    response = RedirectResponse(url="/tracker/dashboard", status_code=302)
    set_tracker_cookie(response)
    return response


@router.post("/logout", include_in_schema=False)
def tracker_logout() -> RedirectResponse:
    _not_enabled()
    response = RedirectResponse(url="/tracker", status_code=302)
    clear_tracker_cookie(response)
    return response


@router.get("/dashboard", response_class=HTMLResponse, include_in_schema=False, response_model=None)
def tracker_dashboard(
    request: Request,
    session: SessionDep,
    page: int = 1,
) -> HTMLResponse | RedirectResponse:
    _not_enabled()
    if not is_tracker_authenticated(request):
        return RedirectResponse(url="/tracker", status_code=302)

    page = max(1, page)
    total = session.scalar(select(func.count()).select_from(RequestLog)) or 0
    unique_ips = session.scalar(select(func.count(func.distinct(RequestLog.client_ip)))) or 0

    stats_rows = session.execute(
        select(RequestLog.path, func.count(RequestLog.id).label("cnt"))
        .group_by(RequestLog.path)
        .order_by(func.count(RequestLog.id).desc())
        .limit(12)
    ).all()

    device_rows = session.execute(
        select(RequestLog.device_kind, func.count(RequestLog.id).label("cnt"))
        .group_by(RequestLog.device_kind)
        .order_by(func.count(RequestLog.id).desc())
    ).all()

    offset = (page - 1) * PAGE_SIZE
    recent = session.scalars(
        select(RequestLog).order_by(RequestLog.created_at.desc()).offset(offset).limit(PAGE_SIZE)
    ).all()

    total_pages = max(1, math.ceil(total / PAGE_SIZE)) if total else 1
    reset_ok = request.query_params.get("reset") == "ok"

    return templates.TemplateResponse(
        request,
        "tracker/dashboard.html",
        {
            "request": request,
            "title": "Usage tracker",
            "total_requests": total,
            "unique_ips": unique_ips,
            "path_stats": stats_rows,
            "device_stats": device_rows,
            "recent": recent,
            "page": page,
            "total_pages": total_pages,
            "page_size": PAGE_SIZE,
            "reset_ok": reset_ok,
        },
    )


@router.get(
    "/reset-data",
    response_class=HTMLResponse,
    include_in_schema=False,
    response_model=None,
)
def tracker_reset_confirm(request: Request) -> HTMLResponse | RedirectResponse:
    _not_enabled()
    if not is_tracker_authenticated(request):
        return RedirectResponse(url="/tracker", status_code=302)
    return templates.TemplateResponse(
        request,
        "tracker/reset_confirm.html",
        {
            "request": request,
            "title": "Reset app data",
            "error": None,
        },
    )


@router.post(
    "/reset-data",
    response_class=HTMLResponse,
    include_in_schema=False,
    response_model=None,
)
def tracker_reset_post(
    request: Request,
    secret: Annotated[str, Form()],
) -> HTMLResponse | RedirectResponse:
    _not_enabled()
    if not is_tracker_authenticated(request):
        return RedirectResponse(url="/tracker", status_code=302)
    expected = app_config.settings.tracker_secret or ""
    if not secrets.compare_digest(secret.strip(), expected.strip()):
        return templates.TemplateResponse(
            request,
            "tracker/reset_confirm.html",
            {
                "request": request,
                "title": "Reset app data",
                "error": "Invalid secret.",
            },
            status_code=401,
        )
    reset_app_data_preserve_request_logs()
    return RedirectResponse(url="/tracker/dashboard?reset=ok", status_code=302)
